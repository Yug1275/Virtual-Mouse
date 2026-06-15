# tests/test_hand_detection.py
# PURPOSE: Test HandDetector and FPSCounter in isolation.

import cv2
import sys
import os

# Add project root to path so we can import our modules.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.hand_detector import HandDetector
from src.utils.fps_counter  import FPSCounter
from config.settings        import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT

def test_hand_detection():
    """
    Opens webcam, runs hand detection, and displays landmarks.
    Press Q to quit.
    """

    print("Initializing HandDetector...")
    detector = HandDetector()
    fps_counter = FPSCounter()

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("ERROR: Cannot open webcam.")
        return

    print("Running hand detection test. Press Q to quit.")
    print("Show your hand to the camera!\n")

    while True:
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)

        # Run hand detection and draw landmarks.
        frame = detector.find_hands(frame)

        # Get landmark positions.
        landmarks = detector.get_landmarks(frame)

        # If hand detected, print index fingertip position (landmark 8).
        if landmarks:
            index_tip = landmarks[8]  # [id, x, y]
            print(f"Index Fingertip → x: {index_tip[1]}, y: {index_tip[2]}", end='\r')

        # Calculate and display FPS.
        fps_text = fps_counter.get_fps_text()
        cv2.putText(frame, fps_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        # Show hand detected status.
        status = "Hand: DETECTED" if detector.is_hand_detected() else "Hand: NOT FOUND"
        color  = (0, 255, 0) if detector.is_hand_detected() else (0, 0, 255)
        cv2.putText(frame, status, (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        cv2.imshow("Hand Detection Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\nTest complete.")


if __name__ == "__main__":
    test_hand_detection()