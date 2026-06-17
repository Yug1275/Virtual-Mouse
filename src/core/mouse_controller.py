# src/core/mouse_controller.py
# PURPOSE: Controls the actual OS mouse cursor using PyAutoGUI.
#          Handles coordinate mapping from camera space to screen space.

import pyautogui
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import (
    FRAME_WIDTH, FRAME_HEIGHT, FRAME_REDUCTION,
    PYAUTOGUI_FAILSAFE, PYAUTOGUI_PAUSE
)


class MouseController:
    """
    Translates hand landmark positions (camera space) into
    actual mouse cursor movement (screen space).

    Usage:
        mouse = MouseController()
        mouse.move_to(cam_x, cam_y)
    """

    def __init__(self):
        """
        Constructor — configures PyAutoGUI and detects screen resolution.
        """

        # Apply our safety settings from config.
        pyautogui.FAILSAFE = PYAUTOGUI_FAILSAFE
        pyautogui.PAUSE    = PYAUTOGUI_PAUSE

        # pyautogui.size() returns (width, height) of the PRIMARY monitor
        # in pixels. This is detected automatically — works on any machine.
        self.screen_width, self.screen_height = pyautogui.size()

        print(f"Detected screen resolution: {self.screen_width}x{self.screen_height}")

    def map_coordinates(self, cam_x, cam_y):
        """
        Maps a camera-space coordinate to a screen-space coordinate,
        accounting for the FRAME_REDUCTION active zone.

        Args:
            cam_x, cam_y: raw pixel position from the camera frame
                          (e.g. landmark 8's x, y in a 640x480 frame)

        Returns:
            (screen_x, screen_y): mapped position on the actual monitor
        """

        # Step 1: Define the active zone boundaries.
        # Example with FRAME_REDUCTION=100 on a 640x480 frame:
        #   active zone X: 100 to 540   (640 - 100)
        #   active zone Y: 100 to 380   (480 - 100)
        active_x_min = FRAME_REDUCTION
        active_x_max = FRAME_WIDTH - FRAME_REDUCTION
        active_y_min = FRAME_REDUCTION
        active_y_max = FRAME_HEIGHT - FRAME_REDUCTION

        # Step 2: Clamp cam_x/cam_y to stay within the active zone.
        # Without this, if your finger goes outside the zone (e.g. near
        # the camera edge), the math below could produce negative
        # or out-of-bounds screen coordinates.
        cam_x = max(active_x_min, min(cam_x, active_x_max))
        cam_y = max(active_y_min, min(cam_y, active_y_max))

        # Step 3: Linear interpolation (np.interp equivalent, done manually).
        # This maps cam_x from range [active_x_min, active_x_max]
        # to range [0, screen_width].
        #
        # Formula: screen_x = (cam_x - active_min) / (active_max - active_min) * screen_width
        screen_x = (cam_x - active_x_min) / (active_x_max - active_x_min) * self.screen_width
        screen_y = (cam_y - active_y_min) / (active_y_max - active_y_min) * self.screen_height

        return screen_x, screen_y

    def move_to(self, cam_x, cam_y):
        """
        Moves the actual OS mouse cursor based on a camera-space coordinate.

        Args:
            cam_x, cam_y: position from camera frame (already smoothed)
        """

        screen_x, screen_y = self.map_coordinates(cam_x, cam_y)

        # pyautogui.moveTo() instantly moves the cursor.
        # duration=0 means no built-in animation — we already smooth
        # ourselves in the Smoother class, so we don't need PyAutoGUI's
        # animation on top of it (that would double-smooth and add lag).
        try:
            pyautogui.moveTo(screen_x, screen_y, duration=0)
        except pyautogui.FailSafeException:
            print("WARNING: Cursor hit screen corner (0,0). Fail-safe triggered.")

    def left_click(self):
        """Performs a single left mouse click at the current cursor position."""
        pyautogui.click(button='left')

    def right_click(self):
        """Performs a single right mouse click at the current cursor position."""
        pyautogui.click(button='right')

    def double_click(self):
        """Performs a double left click at the current cursor position."""
        pyautogui.doubleClick()

    def mouse_down(self):
        """Presses and HOLDS the left mouse button (start of a drag)."""
        pyautogui.mouseDown(button='left')

    def mouse_up(self):
        """Releases the left mouse button (end of a drag)."""
        pyautogui.mouseUp(button='left')

    def scroll(self, amount):
        """
        Scrolls the screen. Positive amount = scroll up, negative = scroll down.
        amount is multiplied by SCROLL_SENSITIVITY for a responsive feel.
        """
        from config.settings import SCROLL_SENSITIVITY
        pyautogui.scroll(int(amount * SCROLL_SENSITIVITY))