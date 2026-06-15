# src/utils/fps_counter.py
# PURPOSE: Calculate and return real-time FPS of the capture loop.

import time  # Python built-in module for time-related functions

class FPSCounter:
    """
    Tracks frames per second by measuring time between calls.

    Usage:
        fps_counter = FPSCounter()
        while True:
            fps = fps_counter.update()
            print(fps)
    """

    def __init__(self):
        """
        Constructor — runs once when you create an FPSCounter object.
        Initializes the two time values we need to calculate FPS.
        """
        # prev_time stores the timestamp of the PREVIOUS frame.
        # We start it at 0 — it gets a real value on the first update() call.
        self.prev_time = 0

        # curr_time stores the timestamp of the CURRENT frame.
        self.curr_time = 0

    def update(self):
        """
        Call this once per frame inside the capture loop.
        Returns the current FPS as a float.
        """

        # time.time() returns the current time in seconds
        # as a float (e.g. 1718123456.342)
        self.curr_time = time.time()

        # FPS formula: how many frames fit in 1 second?
        # If prev→curr took 0.033 seconds → FPS = 1/0.033 = 30 FPS
        # We guard against division by zero with a small epsilon check.
        time_diff = self.curr_time - self.prev_time

        if time_diff == 0:
            fps = 0.0
        else:
            fps = 1.0 / time_diff

        # Save current time as previous for the next frame.
        self.prev_time = self.curr_time

        return fps

    def get_fps_text(self):
        """
        Returns FPS as a formatted string ready to display on screen.
        Example return value: "FPS: 28"
        """
        fps = self.update()
        return f"FPS: {int(fps)}"