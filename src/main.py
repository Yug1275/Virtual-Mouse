# src/main.py
# PURPOSE: Main entry point for Virtual Mouse.
# Phase 4: Adds full gesture-based control (click, drag, scroll).

import cv2
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.hand_detector     import HandDetector
from src.core.mouse_controller  import MouseController
from src.core.gesture_engine    import GestureEngine
from src.utils.fps_counter      import FPSCounter
from src.utils.smoother         import Smoother
from config.settings import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT,
    WINDOW_NAME, TEXT_COLOR, FPS_COLOR,
    FRAME_REDUCTION, SMOOTHING_FACTOR,
    CLICK_COOLDOWN
)


def main():
    print("Virtual Mouse — Phase 4: Full Gesture Control")
    print("Gestures:")
    print("  Index only          -> Move cursor")
    print("  Index+Middle pinch  -> Left click / Drag")
    print("  Index+Middle+Ring   -> Right click")
    print("  Index+Pinky         -> Scroll")
    print("Press Q to quit.\n")

    detector       = HandDetector()
    mouse          = MouseController()
    gesture_engine = GestureEngine()
    fps_counter    = FPSCounter()
    smoother       = Smoother(smoothing_factor=SMOOTHING_FACTOR)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("FATAL: Cannot open webcam.")
        sys.exit(1)

    # Tracks the last time ANY click action fired, to prevent
    # accidental rapid-fire clicks from a single sustained gesture.
    last_action_time = 0

    # Tracks total movement during a drag to distinguish a real drag
    # from a quick tap-click (both start as "drag_start" in our engine).
    drag_start_pos = None
    drag_moved_distance = 0

    while True:
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        frame = detector.find_hands(frame)
        landmarks = detector.get_landmarks(frame)

        cv2.rectangle(
            frame,
            (FRAME_REDUCTION, FRAME_REDUCTION),
            (FRAME_WIDTH - FRAME_REDUCTION, FRAME_HEIGHT - FRAME_REDUCTION),
            (255, 0, 0), 2
        )

        current_time = time.time()

        if landmarks:
            gesture_data = gesture_engine.classify_gesture(landmarks)
            gesture = gesture_data["gesture"]
            cursor_x, cursor_y = gesture_data["cursor_pos"]

            # --- MOVE ---
            if gesture == "move":
                smooth_x, smooth_y = smoother.smooth(cursor_x, cursor_y)
                mouse.move_to(smooth_x, smooth_y)
                cv2.circle(frame, (int(smooth_x), int(smooth_y)), 10, (0, 255, 0), cv2.FILLED)

            # --- DRAG START ---
            elif gesture == "drag_start":
                drag_start_pos = (cursor_x, cursor_y)
                drag_moved_distance = 0
                mouse.mouse_down()
                cv2.circle(frame, (cursor_x, cursor_y), 12, (0, 0, 255), cv2.FILLED)

            # --- DRAG MOVE (continue holding, keep moving cursor) ---
            elif gesture == "drag_move":
                smooth_x, smooth_y = smoother.smooth(cursor_x, cursor_y)
                mouse.move_to(smooth_x, smooth_y)

                if drag_start_pos:
                    import math
                    drag_moved_distance = math.hypot(
                        cursor_x - drag_start_pos[0],
                        cursor_y - drag_start_pos[1]
                    )
                cv2.circle(frame, (int(smooth_x), int(smooth_y)), 12, (0, 0, 255), cv2.FILLED)

            # --- DRAG END (pinch released) ---
            elif gesture in ("drag_end", "double_click"):
                mouse.mouse_up()

                # If the hand barely moved during the "drag", treat it
                # as a simple click instead of a drag — this is how we
                # distinguish a tap from an intentional drag.
                if drag_moved_distance < 15 and (current_time - last_action_time) > CLICK_COOLDOWN:
                    if gesture == "double_click":
                        mouse.double_click()
                        cv2.putText(frame, "DOUBLE CLICK", (10, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    else:
                        mouse.left_click()
                        cv2.putText(frame, "LEFT CLICK", (10, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    last_action_time = current_time

                drag_start_pos = None
                drag_moved_distance = 0

            # --- RIGHT CLICK ---
            elif gesture == "right_click":
                if (current_time - last_action_time) > CLICK_COOLDOWN:
                    mouse.right_click()
                    last_action_time = current_time
                    cv2.putText(frame, "RIGHT CLICK", (10, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

            # --- SCROLL ---
            elif gesture == "scroll":
                scroll_amt = gesture_data["scroll_amount"]
                if scroll_amt != 0:
                    mouse.scroll(scroll_amt)
                    direction = "UP" if scroll_amt > 0 else "DOWN"
                    cv2.putText(frame, f"SCROLL {direction}", (10, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # Show current gesture name for learning/debugging.
            cv2.putText(frame, f"Gesture: {gesture}", (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT_COLOR, 2)

        else:
            # Hand left the frame — reset all stateful trackers.
            smoother.reset()
            gesture_engine.reset()
            drag_start_pos = None

        fps_text = fps_counter.get_fps_text()
        cv2.putText(frame, fps_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, FPS_COLOR, 2)

        cv2.imshow(WINDOW_NAME, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Virtual Mouse stopped.")


if __name__ == "__main__":
    main()