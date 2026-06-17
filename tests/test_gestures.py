# tests/test_gestures.py
# PURPOSE: Test GestureEngine logic with simulated landmark data,
#          without needing a webcam. Pure logic testing.

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.gesture_engine import GestureEngine


def make_fake_landmarks(finger_states):
    """
    Builds a fake 21-landmark list where specific fingers are 'up'.
    finger_states: dict like {"index": True, "middle": False, ...}

    This lets us test gesture logic WITHOUT a real camera or hand.
    """
    landmarks = [[i, 300, 300] for i in range(21)]  # default: all folded near center

    if finger_states.get("index"):
        landmarks[8] = [8, 300, 100]   # tip far above pip → "up"
        landmarks[6] = [6, 300, 250]
    if finger_states.get("middle"):
        landmarks[12] = [12, 320, 100]
        landmarks[10] = [10, 320, 250]
    if finger_states.get("ring"):
        landmarks[16] = [16, 340, 100]
        landmarks[14] = [14, 340, 250]
    if finger_states.get("pinky"):
        landmarks[20] = [20, 360, 100]
        landmarks[18] = [18, 360, 250]

    return landmarks


def test_move_gesture():
    engine = GestureEngine()
    landmarks = make_fake_landmarks({"index": True})
    result = engine.classify_gesture(landmarks)
    print(f"Move test       -> gesture: {result['gesture']} (expected: move)")


def test_scroll_gesture():
    engine = GestureEngine()
    landmarks = make_fake_landmarks({"index": True, "pinky": True})
    result = engine.classify_gesture(landmarks)
    print(f"Scroll test     -> gesture: {result['gesture']} (expected: scroll)")


def test_finger_states():
    engine = GestureEngine()
    landmarks = make_fake_landmarks({"index": True, "middle": True})
    states = engine.get_finger_states(landmarks)
    print(f"Finger states   -> {states} (expected: [_, 1, 1, 0, 0])")


if __name__ == "__main__":
    print("Running gesture engine tests (no camera needed)...\n")
    test_finger_states()
    test_move_gesture()
    test_scroll_gesture()
    print("\nAll tests executed. Verify outputs match expected values.")