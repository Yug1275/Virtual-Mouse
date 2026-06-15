# Phase 1 — Webcam Capture Notes

## What I learned
- Video = sequence of frames captured in a loop
- cap = cv2.VideoCapture(0) connects to default webcam
- cap.read() returns (success, frame) every iteration
- Frame is a NumPy array of shape (height, width, 3)
- OpenCV uses BGR color order, not RGB
- cv2.flip(frame, 1) mirrors the frame horizontally
- Always call cap.release() and cv2.destroyAllWindows() on exit
- cv2.waitKey(1) is required to actually render the window

## Why we flip
Without flip: moving hand right = cursor goes left (confusing)
With flip: acts like a mirror (natural)

## Why 640x480
Good FPS vs detail tradeoff. We'll keep this throughout the project.

## Used in: All future phases (main loop pattern stays the same)