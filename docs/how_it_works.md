# How Virtual Mouse Works

This document explains the internal architecture for developers
(including future-you) who want to understand the system without
reading every line of code.

## Pipeline Overview

Webcam → OpenCV (capture/flip) → MediaPipe (21 landmarks) →
GestureEngine (classify) → MouseController (PyAutoGUI) → OS cursor

## Module Responsibilities

- `hand_detector.py`    : Wraps MediaPipe. Input: BGR frame. Output: 21 landmark pixel coords.
- `gesture_engine.py`   : Pure logic. Input: landmarks. Output: gesture name + data. No camera/OS dependency.
- `mouse_controller.py` : Wraps PyAutoGUI. Converts camera coords to screen coords. Executes OS-level mouse actions.
- `smoother.py`         : Pure math. Exponential moving average for jitter reduction.
- `fps_counter.py`      : Pure math. Tracks frame timing.
- `logger.py`           : Centralized logging setup, used by all modules.
- `settings.py`         : Single source of truth for all tunable values. Includes validate_settings().
- `main.py`             : Orchestrates everything. Owns the camera loop, error handling, and shutdown.

## Why This Structure?

Each module can be tested independently (see tests/ folder) because
none of them depend on the webcam being open. GestureEngine, for
example, is tested with fake landmark data — no camera needed.

## State That Persists Across Frames

- `Smoother`: remembers previous cursor position
- `GestureEngine`: remembers drag state, click timestamps, right-click hold start
- Both have a `.reset()` method called when the hand leaves the frame,
  preventing stale state from causing incorrect behavior when the hand returns.

## Error Handling Philosophy

- Single bad frame → log warning, continue loop
- Many bad frames in a row → log error, exit cleanly
- Bad config at startup → fail immediately with a clear message (fail fast)
- Unexpected crash → caught at top level, logged with full traceback, camera still released via `finally`

## Extending This Project

To add a new gesture:
1. Add finger-state logic to `gesture_engine.classify_gesture()`
2. Add a corresponding case in `main.py`'s gesture handling block
3. Add any new settings (thresholds) to `config/settings.py`
4. Add a test case to `tests/test_gestures.py`