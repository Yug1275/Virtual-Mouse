# Phase 0 — Project Planning Notes

## Purpose
Document the planning decisions made before writing any code.

## Tech Stack Decisions
- OpenCV: webcam capture and display
- MediaPipe: hand landmark detection
- PyAutoGUI: mouse/keyboard control
- NumPy: coordinate math

## Architecture Decision
Separated into core/, utils/, config/ to keep concerns isolated.
Each module has one responsibility (Single Responsibility Principle).

## Key Landmarks
- Landmark 8  = Index fingertip (cursor movement)
- Landmark 4  = Thumb tip (click detection)
- Landmark 12 = Middle fingertip (gesture help)

## Used in: Phase 1 onwards (reference)