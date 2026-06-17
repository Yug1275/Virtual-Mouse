# src/core/gesture_engine.py
# PURPOSE: Classify hand gestures from MediaPipe landmarks.
#          Tracks state across frames (e.g. for drag and double-click).

import math
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import (
    CLICK_DISTANCE_THRESHOLD,
    CLICK_COOLDOWN,
    DOUBLE_CLICK_WINDOW,
    RIGHT_CLICK_HOLD_TIME,
    SCROLL_DEAD_ZONE
)

# Landmark ID constants — using names instead of raw numbers makes
# the code self-documenting. Anyone reading "INDEX_TIP" instantly
# understands it without memorizing "8".
THUMB_TIP   = 4
INDEX_TIP   = 8
INDEX_PIP   = 6
MIDDLE_TIP  = 12
MIDDLE_PIP  = 10
RING_TIP    = 16
RING_PIP    = 14
PINKY_TIP   = 20
PINKY_PIP   = 18


class GestureEngine:
    """
    Analyzes hand landmarks frame-by-frame and determines:
      - Current finger up/down states
      - Which gesture is active (move, click, drag, scroll)

    Maintains state across frames for drag detection and double-click timing.
    """

    def __init__(self):
        # --- State for click cooldown ---
        self.last_click_time = 0       # timestamp of the most recent left click

        # --- State for double-click detection ---
        self.click_times = []          # list of recent click timestamps

        # --- State for drag ---
        self.is_dragging = False       # True while a drag is in progress

        # --- State for right click (needs hold time) ---
        self.right_click_gesture_start = None  # when right-click gesture began

        # --- State for scroll (needs previous hand Y to compute direction) ---
        self.prev_scroll_y = None

    # ------------------------------------------------------------------
    # FINGER STATE DETECTION
    # ------------------------------------------------------------------

    def get_finger_states(self, landmarks):
        """
        Returns a list of 5 values [thumb, index, middle, ring, pinky]
        where 1 = finger extended (up), 0 = finger folded (down).

        landmarks: list of [id, x, y] from HandDetector.get_landmarks()
        """

        fingers = []

        # THUMB — special case: compares X instead of Y because thumb
        # moves sideways, not vertically, relative to the palm.
        # We compare thumb tip(4) X position to thumb IP joint(3) X position.
        # Since the frame is already mirrored (flipped), thumb extended
        # to the LEFT means thumb_tip.x < thumb_ip.x for a right hand.
        thumb_tip_x = landmarks[THUMB_TIP][1]
        thumb_ip_x  = landmarks[3][1]
        fingers.append(1 if thumb_tip_x < thumb_ip_x else 0)

        # INDEX, MIDDLE, RING, PINKY — all compare tip.y to pip.y.
        # Smaller y = higher on screen = finger extended upward.
        finger_pairs = [
            (INDEX_TIP, INDEX_PIP),
            (MIDDLE_TIP, MIDDLE_PIP),
            (RING_TIP, RING_PIP),
            (PINKY_TIP, PINKY_PIP),
        ]

        for tip_id, pip_id in finger_pairs:
            tip_y = landmarks[tip_id][2]
            pip_y = landmarks[pip_id][2]
            fingers.append(1 if tip_y < pip_y else 0)

        return fingers  # e.g. [0, 1, 0, 0, 0] = only index up

    # ------------------------------------------------------------------
    # DISTANCE HELPER
    # ------------------------------------------------------------------

    def get_distance(self, landmarks, id1, id2):
        """
        Calculates Euclidean (straight-line) distance between two landmarks.
        Used for pinch detection (thumb-index distance).
        """
        x1, y1 = landmarks[id1][1], landmarks[id1][2]
        x2, y2 = landmarks[id2][1], landmarks[id2][2]

        # Pythagorean theorem: distance = sqrt(dx^2 + dy^2)
        distance = math.hypot(x2 - x1, y2 - y1)
        return distance

    # ------------------------------------------------------------------
    # GESTURE CLASSIFICATION
    # ------------------------------------------------------------------

    def classify_gesture(self, landmarks):
        """
        Main classification method. Call this once per frame.

        Returns a dictionary describing what's happening this frame:
        {
            "gesture": "move" | "left_click" | "right_click" |
                       "double_click" | "drag_start" | "drag_move" |
                       "drag_end" | "scroll" | "none",
            "cursor_pos": (x, y)        # index fingertip position, for moving
            "scroll_amount": int        # only present for "scroll"
        }
        """

        fingers = self.get_finger_states(landmarks)
        thumb, index, middle, ring, pinky = fingers

        index_pos = (landmarks[INDEX_TIP][1], landmarks[INDEX_TIP][2])
        current_time = time.time()

        result = {
            "gesture": "none",
            "cursor_pos": index_pos,
            "scroll_amount": 0
        }

        # ---------------------------------------------------------
        # PRIORITY ORDER MATTERS: check more specific gestures first.
        # ---------------------------------------------------------

        # --- SCROLL: index + pinky up, middle + ring down ---
        if index == 1 and pinky == 1 and middle == 0 and ring == 0:
            result["gesture"] = "scroll"
            result["scroll_amount"] = self._calculate_scroll(landmarks)
            return result

        # --- RIGHT CLICK: index + middle + ring up, thumb/pinky down ---
        if index == 1 and middle == 1 and ring == 1 and pinky == 0:
            if self.right_click_gesture_start is None:
                self.right_click_gesture_start = current_time

            held_duration = current_time - self.right_click_gesture_start

            if held_duration >= RIGHT_CLICK_HOLD_TIME:
                result["gesture"] = "right_click"
                self.right_click_gesture_start = None  # reset after firing
            return result
        else:
            # Gesture broken before hold time reached — reset timer.
            self.right_click_gesture_start = None

        # --- LEFT CLICK / DRAG: index + middle up, then pinch thumb-index ---
        if index == 1 and middle == 1:
            pinch_distance = self.get_distance(landmarks, THUMB_TIP, INDEX_TIP)
            is_pinching = pinch_distance < CLICK_DISTANCE_THRESHOLD

            if is_pinching and not self.is_dragging:
                # Pinch just started — could become a click OR a drag.
                # We optimistically start a drag; if released quickly,
                # main.py / mouse_controller treats it as a click.
                self.is_dragging = True
                result["gesture"] = "drag_start"
                return result

            elif is_pinching and self.is_dragging:
                # Pinch continues — ongoing drag.
                result["gesture"] = "drag_move"
                return result

            elif not is_pinching and self.is_dragging:
                # Pinch released — end the drag.
                self.is_dragging = False
                result["gesture"] = "drag_end"

                # Check cooldown — was this a quick tap (click) or
                # a genuine drag? Either way, mouse_controller decides
                # based on how much movement happened during drag_move.
                # Here we also register it for double-click tracking.
                self._register_click(current_time)
                if self._is_double_click(current_time):
                    result["gesture"] = "double_click"

                return result

        # --- MOVE: only index finger up ---
        if index == 1 and middle == 0:
            result["gesture"] = "move"
            return result

        return result

    # ------------------------------------------------------------------
    # SCROLL HELPER
    # ------------------------------------------------------------------

    def _calculate_scroll(self, landmarks):
        """
        Determines scroll direction and magnitude based on vertical
        hand movement while the scroll gesture is held.
        """
        current_y = landmarks[INDEX_TIP][2]

        if self.prev_scroll_y is None:
            self.prev_scroll_y = current_y
            return 0

        delta_y = self.prev_scroll_y - current_y  # positive = moved up

        # Ignore tiny movements (hand isn't perfectly still).
        if abs(delta_y) < SCROLL_DEAD_ZONE:
            return 0

        self.prev_scroll_y = current_y
        return delta_y  # positive = scroll up, negative = scroll down

    # ------------------------------------------------------------------
    # CLICK / DOUBLE-CLICK TRACKING
    # ------------------------------------------------------------------

    def _register_click(self, current_time):
        """Records a click timestamp for double-click detection."""
        self.click_times.append(current_time)
        # Keep only the last 2 click times — we don't need more history.
        self.click_times = self.click_times[-2:]

    def _is_double_click(self, current_time):
        """
        Checks if the last two registered clicks happened within
        DOUBLE_CLICK_WINDOW seconds of each other.
        """
        if len(self.click_times) < 2:
            return False

        time_between = self.click_times[-1] - self.click_times[-2]
        return time_between <= DOUBLE_CLICK_WINDOW

    def reset(self):
        """
        Resets all gesture state. Call this when the hand disappears
        from the frame, so stale state doesn't cause false gestures
        when the hand reappears.
        """
        self.is_dragging = False
        self.right_click_gesture_start = None
        self.prev_scroll_y = None