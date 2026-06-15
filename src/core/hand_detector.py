# src/core/hand_detector.py
# PURPOSE: Detect hand landmarks using MediaPipe.
#          Wraps MediaPipe Hands into a clean, reusable class.

import cv2          # OpenCV — for color conversion (BGR to RGB)
import mediapipe as mp  # Google's MediaPipe framework
import sys
import os

# We need to import from config/settings.py.
# But Python needs to know where to find it.
# This adds the project ROOT folder to Python's search path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import (
    MAX_HANDS,
    DETECTION_CONF,
    TRACKING_CONF,
    LANDMARK_COLOR,
    CONNECTION_COLOR
)


class HandDetector:
    """
    Detects and tracks hand landmarks using MediaPipe Hands.

    Usage:
        detector = HandDetector()
        frame = detector.find_hands(frame)
        landmarks = detector.get_landmarks(frame)
    """

    def __init__(self):
        """
        Constructor — initializes MediaPipe Hands model.
        This loads the ML model into memory. Do this ONCE, not per frame.
        """

        # mp.solutions is MediaPipe's collection of pre-built ML solutions.
        # mp.solutions.hands gives us the Hands solution specifically.
        self.mp_hands = mp.solutions.hands

        # mp.solutions.drawing_utils has helper functions to draw
        # landmarks and connections on frames automatically.
        self.mp_draw  = mp.solutions.drawing_utils

        # mp.solutions.drawing_styles provides default visual styles
        # for drawing landmarks (colors, thickness, etc.)
        self.mp_styles = mp.solutions.drawing_styles

        # Initialize the Hands model with our settings.
        # static_image_mode=False → treat input as video stream (uses tracking)
        #                  =True  → treat each image independently (slower)
        # max_num_hands    → maximum number of hands to detect
        # min_detection_confidence → how confident MediaPipe must be to
        #                            say "yes, there's a hand here"
        # min_tracking_confidence  → how confident it must be to keep
        #                            tracking an already-detected hand
        self.hands = self.mp_hands.Hands(
            static_image_mode        = False,
            max_num_hands            = MAX_HANDS,
            min_detection_confidence = DETECTION_CONF,
            min_tracking_confidence  = TRACKING_CONF
        )

        # Store the last detected landmark list so other methods can use it.
        # Starts as None because no frame has been processed yet.
        self.landmark_list = []

    def find_hands(self, frame, draw=True):
        """
        Process a frame and detect hands.
        Optionally draws landmarks and connections on the frame.

        Args:
            frame : BGR image (NumPy array) from OpenCV
            draw  : if True, draws landmarks on the frame

        Returns:
            frame : same frame, with landmarks drawn (if draw=True)
        """

        # MediaPipe requires RGB input.
        # OpenCV gives us BGR.
        # cv2.COLOR_BGR2RGB converts it.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # process() runs the hand detection ML model on the frame.
        # It returns a Results object containing:
        #   .multi_hand_landmarks → list of detected hands, each with 21 landmarks
        #   .multi_handedness     → list of hand labels (Left/Right) with confidence
        self.results = self.hands.process(rgb_frame)

        # multi_hand_landmarks is None if no hand is detected.
        # We only draw if it's not None.
        if self.results.multi_hand_landmarks and draw:

            # Loop over each detected hand (we configured max 1, but good practice).
            for hand_landmarks in self.results.multi_hand_landmarks:

                # draw_landmarks() draws:
                #   - A dot at each of the 21 landmark positions
                #   - Lines connecting landmarks (the "skeleton")
                # HAND_CONNECTIONS is MediaPipe's built-in list of which
                # landmarks should be connected with lines.
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    # Style for the landmark DOTS
                    self.mp_draw.DrawingSpec(
                        color     = LANDMARK_COLOR,
                        thickness = 2,
                        circle_radius = 4
                    ),
                    # Style for the CONNECTION LINES
                    self.mp_draw.DrawingSpec(
                        color     = CONNECTION_COLOR,
                        thickness = 2
                    )
                )

        return frame

    def get_landmarks(self, frame):
        """
        After calling find_hands(), call this to get landmark pixel positions.

        Returns:
            list of [id, x, y] for each of the 21 landmarks.
            Empty list if no hand detected.

        Example return:
            [
              [0, 320, 400],   ← WRIST at pixel (320, 400)
              [1, 310, 370],
              ...
              [20, 290, 200],  ← PINKY TIP
            ]
        """

        self.landmark_list = []

        # If no hand was detected in the last find_hands() call, return empty.
        if not self.results.multi_hand_landmarks:
            return self.landmark_list

        # Get the first detected hand (index 0).
        # Since MAX_HANDS=1, there's only ever one hand anyway.
        hand = self.results.multi_hand_landmarks[0]

        # frame.shape returns (height, width, channels).
        # We need height and width to convert normalized coords → pixels.
        h, w, _ = frame.shape

        # enumerate() gives us both the index (id) and the landmark object.
        for landmark_id, landmark in enumerate(hand.landmark):

            # Convert normalized (0.0-1.0) coords to actual pixel positions.
            pixel_x = int(landmark.x * w)
            pixel_y = int(landmark.y * h)

            # Append [id, x, y] to our list.
            self.landmark_list.append([landmark_id, pixel_x, pixel_y])

        return self.landmark_list

    def is_hand_detected(self):
        """
        Quick check — returns True if a hand is currently detected.
        Useful to avoid processing when no hand is in frame.
        """
        return bool(
            self.results.multi_hand_landmarks
            if hasattr(self, 'results') else False
        )