# src/main.py
# PURPOSE: Main entry point for Virtual Mouse.
# Phase 2: Integrates HandDetector and FPSCounter.

import cv2
import sys
import os

# Add project root to Python path.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.hand_detector import HandDetector
from src.utils.fps_counter  import FPSCounter
from config.settings        import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT,
    WINDOW_NAME, TEXT_COLOR, FPS_COLOR
)


def main():
    print("Virtual Mouse — Phase 2: Hand Detection")
    print("Show your hand to the camera!")
    print("Press Q to quit.\n")

    # Initialize modules — each is a single responsibility.
    detector    = HandDetector()
    fps_counter = FPSCounter()

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("FATAL: Cannot open webcam.")
        sys.exit(1)

    while True:
        success, frame = cap.read()
        if not success:
            continue

        # Mirror the frame.
        frame = cv2.flip(frame, 1)

        # Step 1: Detect and draw hand landmarks.
        frame = detector.find_hands(frame)

        # Step 2: Get landmark pixel positions.
        landmarks = detector.get_landmarks(frame)

        # Step 3: Show index fingertip position if hand detected.
        if landmarks:
            tip = landmarks[8]  # Index fingertip
            cv2.putText(
                frame,
                f"Index Tip → ({tip[1]}, {tip[2]})",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, TEXT_COLOR, 2
            )

        # Step 4: Display FPS.
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