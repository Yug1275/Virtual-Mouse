# System Architecture

## Data Flow
Webcam → OpenCV → MediaPipe → Gesture Engine → PyAutoGUI → Screen

## Module Responsibilities
- hand_detector.py   : wraps MediaPipe, returns landmark list
- gesture_engine.py  : takes landmarks, returns gesture name
- mouse_controller.py: takes gesture + position, calls PyAutoGUI
- fps_counter.py     : calculates and returns FPS value
- smoother.py        : smooths x,y coordinates over time
- settings.py        : all magic numbers live here (sensitivity, etc.)
- main.py            : orchestrates all modules in a loop

## Used in: All phases (living document, update as project grows)