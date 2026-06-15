# tests/test_camera.py
# PURPOSE: Verify that OpenCV can access the webcam successfully.
# This is a standalone test — not part of the main project flow.

import cv2  # OpenCV library for computer vision tasks

def test_camera():
    """
    Opens the default webcam, prints camera properties,
    and displays a live feed for 5 seconds then exits.
    """

    # cv2.VideoCapture(0) connects to your default webcam.
    # 0 = first camera. If you have multiple cameras, try 1, 2, etc.
    cap = cv2.VideoCapture(0)

    # Always check if the camera opened successfully.
    # If the camera is in use by another app, this will be False.
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        print("Possible reasons:")
        print("  - Webcam is being used by another application")
        print("  - Webcam driver is not installed")
        print("  - Wrong camera index (try 1 instead of 0)")
        return  # Exit the function early

    # Read camera properties AFTER confirming it opened.
    # CAP_PROP_FRAME_WIDTH  = width of each frame in pixels
    # CAP_PROP_FRAME_HEIGHT = height of each frame in pixels
    # CAP_PROP_FPS          = frames per second the camera supports
    width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps    = cap.get(cv2.CAP_PROP_FPS)

    print(f"Camera opened successfully!")
    print(f"Resolution : {int(width)} x {int(height)}")
    print(f"FPS        : {fps}")

    print("\nDisplaying webcam feed...")
    print("Press 'Q' to quit early.")

    # --- THE CAPTURE LOOP ---
    # This loop runs continuously, reading one frame per iteration.
    while True:

        # cap.read() does two things:
        #   success (bool) : True if the frame was captured without error
        #   frame (numpy array) : the actual image as a 3D array
        #                         shape = (height, width, 3 color channels)
        success, frame = cap.read()

        # If frame capture failed (camera disconnected, etc.), stop.
        if not success:
            print("ERROR: Failed to read frame from webcam.")
            break

        # cv2.imshow(window_name, frame) opens a window and displays the frame.
        # "Webcam Test" is the title of the window.
        cv2.imshow("Webcam Test", frame)

        # cv2.waitKey(1) waits 1 millisecond for a key press.
        # It returns the ASCII value of the key pressed, or -1 if none.
        # ord('q') = ASCII value of 'q' = 113
        # 0xFF is a bitmask used for compatibility across systems.
        # This means: "if the user presses Q, break out of the loop"
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Q pressed. Exiting...")
            break

    # ALWAYS release the camera and destroy windows when done.
    # If you skip this, the camera stays locked and other apps can't use it.
    cap.release()
    cv2.destroyAllWindows()
    print("Camera released. Test complete.")


# This block only runs when you execute THIS file directly.
# It will NOT run if this file is imported by another file.
# Good practice for all test and utility scripts.
if __name__ == "__main__":
    test_camera()