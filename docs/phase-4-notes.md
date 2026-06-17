# Phase 4 — Gesture Engine Notes

## What I learned
- Finger "up" detection: compare tip.y to pip.y (smaller y = higher = up)
- Thumb is special: compares x, not y, since it moves sideways
- Euclidean distance (math.hypot) detects pinch gestures
- Gesture priority order matters — check specific gestures before generic ones
- Stateful gestures (drag) need a class with self.is_dragging memory
- Cooldowns prevent one held gesture from firing multiple click events
- Double-click = two clicks within DOUBLE_CLICK_WINDOW seconds
- Drag vs Click distinguished by how much the hand moved during the pinch
- gesture_engine.reset() prevents stale state when hand reappears

## Gesture vocabulary (final)
- Index only          -> Move
- Index+Middle pinch   -> Left click (or Drag if held+moved)
- Index+Middle+Ring    -> Right click (needs hold time)
- Index+Pinky          -> Scroll (vertical hand movement)
- Two pinches quickly  -> Double click

## Used in: Phase 5 (final polish, error handling, packaging)