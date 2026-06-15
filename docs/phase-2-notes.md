# Phase 2 — Hand Detection Notes

## What I learned
- MediaPipe Hands detects 21 landmarks per hand
- Landmarks are normalized (0.0-1.0), must multiply by frame w/h for pixels
- MediaPipe needs RGB input; OpenCV gives BGR → must convert
- static_image_mode=False enables tracking (faster for video)
- Landmark 8 = Index fingertip (our cursor control point)
- Fingertips are landmarks: 4, 8, 12, 16, 20
- FPS = 1 / time_between_frames
- sys.path.append() lets Python find our modules across folders

## Key landmark IDs (memorize)
- 0  = Wrist
- 4  = Thumb tip
- 8  = Index tip  ← cursor
- 12 = Middle tip
- 16 = Ring tip
- 20 = Pinky tip

## Used in: Phase 3 (cursor), Phase 4 (gestures) — landmark list is everything