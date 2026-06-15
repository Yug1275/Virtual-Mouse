# src/main.py
# PURPOSE: Main entry point for the Virtual Mouse application.
# Each phase will add more functionality to this file.
# Phase 1: Basic webcam capture and display only.

import cv2      # OpenCV — for capturing and displaying video
import sys      # Python built-in — for clean program exit with error codes

def main():
    """
    Main application loop.
    Phase 1: Opens webcam, displays feed, exits on Q key.
    """

    print("Virtual Mouse — Starting...")
    print("Press 'Q' to quit.\n")

    # Connect to the default webcam (index 0).
    cap = cv2.VideoCapture(0)

    # Verify the webcam opened. Exit with an error code if not.
    if not cap.isOpened():
        print("FATAL ERROR: Cannot open webcam.")
        print("Run tests/test_camera.py for detailed diagnostics.")
        sys.exit(1)  # Exit code 1 = error. Exit code 0 = success.

    # Set the webcam resolution explicitly.
    # 640x480 is a good balance — high enough to see hand details,
    # low enough to process at 30+ FPS without lag.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("Webcam opened. Starting capture loop...")

    # --- MAIN CAPTURE LOOP ---
    while True:

        # Read one frame from the webcam.
        success, frame = cap.read()

        if not success:
            print("Warning: Missed a frame. Retrying...")
            continue  # Skip this iteration and try again (don't break)

        # FLIP the frame horizontally (mirror effect).
        # Why? Without this, moving your RIGHT hand moves the cursor LEFT.
        # Flipping makes it feel natural — like looking in a mirror.
        # cv2.flip(frame, 1) → 1 = horizontal flip
        frame = cv2.flip(frame, 1)

        # Display the frame count and resolution on the frame itself.
        # cv2.putText(image, text, position, font, scale, color, thickness)
        # cv2.FONT_HERSHEY_SIMPLEX = a clean, readable font
        # (10, 30) = position from top-left corner (x=10, y=30)
        # (0, 255, 0) = green color in BGR format
        cv2.putText(
            frame,
            "Phase 1: Webcam Active | Press Q to quit",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,           # font scale (size)
            (0, 255, 0),   # color: green (BGR)
            2              # thickness in pixels
        )

        # Show the frame in a window titled "Virtual Mouse".
        cv2.imshow("Virtual Mouse", frame)

        # Wait 1ms for keypress. Quit if 'Q' is pressed.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Q pressed. Shutting down...")
            break

    # Cleanup — always do this before exiting.
    cap.release()
    cv2.destroyAllWindows()
    print("Virtual Mouse stopped.")


# Only run main() when this file is executed directly.
if __name__ == "__main__":
    main()