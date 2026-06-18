# Virtual Mouse using Hand Gestures

Control your computer's mouse cursor using hand gestures captured
via webcam — no physical mouse required.

## Features

- Cursor movement via index finger tracking
- Left click, right click, and double click gestures
- Drag and drop support
- Scroll up/down gesture
- Real-time FPS display and hand landmark visualization
- Configurable sensitivity and gesture thresholds
- Robust error handling and logging

## Tech Stack

Python, OpenCV, MediaPipe, PyAutoGUI, NumPy

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py
```

## Gesture Guide

| Gesture | Action |
|---|---|
| Index finger only | Move cursor |
| Index + Middle, pinch thumb-index | Left click |
| Pinch + hold + move | Drag and drop |
| Index + Middle + Ring, hold | Right click |
| Two quick pinches | Double click |
| Index + Pinky, move hand vertically | Scroll |

Press **Q** in the application window to quit.

## Configuration

All tunable values live in `config/settings.py`:
- `SMOOTHING_FACTOR` — cursor smoothness vs responsiveness
- `FRAME_REDUCTION` — size of the active control zone
- `CLICK_DISTANCE_THRESHOLD` — pinch sensitivity
- `SCROLL_SENSITIVITY` — scroll speed

## Project Structure

See `docs/how_it_works.md` for full architecture details.

## Logs

Runtime logs are saved to `logs/app.log` for debugging.

## Development Phases

- [x] Phase 0 — Planning & Setup
- [x] Phase 1 — Webcam Capture
- [x] Phase 2 — Hand Detection
- [x] Phase 3 — Cursor Movement & Smoothing
- [x] Phase 4 — Gesture Recognition
- [x] Phase 5 — Error Handling & Polish

## Testing

Each module has an isolated test in `tests/`:
```powershell
python tests/test_camera.py
python tests/test_hand_detection.py
python tests/test_cursor_movement.py
python tests/test_gestures.py
python tests/test_config_validation.py
```