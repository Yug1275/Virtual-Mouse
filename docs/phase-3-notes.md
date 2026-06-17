# Phase 3 — Cursor Movement Notes

## What I learned
- Camera resolution != screen resolution → coordinates must be mapped
- FRAME_REDUCTION creates a comfortable "active zone" smaller than the full frame
- Linear interpolation formula: (val - min)/(max - min) * target_range
- Raw landmark coordinates jitter frame-to-frame due to detection noise
- Exponential Moving Average smooths jitter: prev + (new-prev)/factor
- Higher smoothing_factor = smoother but more lag; tune via settings.py
- pyautogui.size() auto-detects screen resolution — works cross-machine
- pyautogui.FAILSAFE: moving cursor to (0,0) raises an exception (safety net)
- duration=0 in moveTo() avoids double-smoothing (we already smooth ourselves)
- smoother.reset() prevents cursor jump when hand reappears at new position

## Used in: Phase 4 (gestures will use the same landmark + mapping pipeline)