# src/main.py
# PURPOSE: Main entry point for Virtual Mouse.
# Phase 3: Adds cursor movement with smoothing.

import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.hand_detector     import HandDetector
from src.core.mouse_controller  import MouseController
from src.utils.fps_counter      import FPSCounter
from src.utils.smoother         import Smoother
from config.settings import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT,
    WINDOW_NAME, TEXT_COLOR, FPS_COLOR,
    FRAME_REDUCTION, SMOOTHING_FACTOR
)


def main():
    print("Virtual Mouse — Phase 3: Cursor Movement")
    print("Move your INDEX finger to control the cursor.")
    print("Press Q to quit.\n")

    detector    = HandDetector()
    mouse       = MouseController()
    fps_counter = FPSCounter()
    smoother    = Smoother(smoothing_factor=SMOOTHING_FACTOR)

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

        frame = cv2.flip(frame, 1)
        frame = detector.find_hands(frame)
        landmarks = detector.get_landmarks(frame)

        # Draw the "active zone" rectangle so you can SEE where to move
        # your hand for full screen coverage. Purely visual — for learning.
        cv2.rectangle(
            frame,
            (FRAME_REDUCTION, FRAME_REDUCTION),
            (FRAME_WIDTH - FRAME_REDUCTION, FRAME_HEIGHT - FRAME_REDUCTION),
            (255, 0, 0),  # Blue box
            2
        )

        if landmarks:
            # Landmark 8 = index fingertip.
            index_x, index_y = landmarks[8][1], landmarks[8][2]

            # Smooth the raw coordinate to eliminate jitter.
            smooth_x, smooth_y = smoother.smooth(index_x, index_y)

            # Move the actual OS cursor.
            mouse.move_to(smooth_x, smooth_y)

            # Visual feedback: draw a circle at the smoothed fingertip position.
            cv2.circle(frame, (int(smooth_x), int(smooth_y)), 10, (0, 255, 0), cv2.FILLED)

            cv2.putText(
                frame, f"Index: ({index_x}, {index_y})",
                (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT_COLOR, 2
            )
        else:
            # If hand disappears, reset the smoother so the cursor doesn't
            # jump erratically when the hand reappears at a new position.
            smoother.reset()

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