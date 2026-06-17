# tests/test_cursor_movement.py
# PURPOSE: Isolated test for coordinate mapping and smoothing math,
#          without needing the full hand detection pipeline.

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.mouse_controller import MouseController
from src.utils.smoother import Smoother


def test_mapping():
    """
    Tests that map_coordinates() correctly maps known camera
    coordinates to expected screen coordinates.
    """
    mouse = MouseController()

    # Test case: center of the active zone should map to
    # roughly the center of the screen.
    cam_center_x = 320  # center of 640 width
    cam_center_y = 240  # center of 480 height

    screen_x, screen_y = mouse.map_coordinates(cam_center_x, cam_center_y)

    print(f"Camera center (320, 240) → Screen ({screen_x:.0f}, {screen_y:.0f})")
    print(f"Expected approx: ({mouse.screen_width/2:.0f}, {mouse.screen_height/2:.0f})")


def test_smoothing():
    """
    Tests that the Smoother gradually approaches a target value
    rather than jumping instantly.
    """
    smoother = Smoother(smoothing_factor=5)

    print("\nSimulating jump from (0,0) to (100,100):")
    for i in range(8):
        x, y = smoother.smooth(100, 100)
        print(f"  Step {i+1}: ({x:.1f}, {y:.1f})")


if __name__ == "__main__":
    test_mapping()
    test_smoothing()