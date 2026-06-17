# src/utils/smoother.py
# PURPOSE: Smooth out jittery coordinate values using exponential moving average.

class Smoother:
    """
    Smooths a stream of (x, y) coordinates over time to eliminate jitter.

    Usage:
        smoother = Smoother(smoothing_factor=5)
        smooth_x, smooth_y = smoother.smooth(raw_x, raw_y)
    """

    def __init__(self, smoothing_factor=5):
        """
        Args:
            smoothing_factor: Higher = smoother but more delayed response.
                               Lower  = faster but more jittery.
        """
        self.smoothing_factor = smoothing_factor

        # Previous smoothed position. Starts at None because
        # we haven't received any coordinates yet.
        self.prev_x = None
        self.prev_y = None

    def smooth(self, new_x, new_y):
        """
        Takes a new raw (x, y) coordinate and returns a smoothed version.

        The formula: prev + (new - prev) / smoothing_factor

        This means: move only a FRACTION of the distance toward the
        new target each frame, instead of jumping there instantly.
        """

        # On the very first call, there's no previous position yet.
        # So we just accept the new position as-is (no smoothing possible).
        if self.prev_x is None or self.prev_y is None:
            self.prev_x = new_x
            self.prev_y = new_y
            return new_x, new_y

        # Exponential Moving Average formula.
        smooth_x = self.prev_x + (new_x - self.prev_x) / self.smoothing_factor
        smooth_y = self.prev_y + (new_y - self.prev_y) / self.smoothing_factor

        # Save this smoothed value as "previous" for the next call.
        self.prev_x = smooth_x
        self.prev_y = smooth_y

        return smooth_x, smooth_y

    def reset(self):
        """
        Resets the smoother's memory.
        Useful when the hand disappears and reappears — prevents the
        cursor from jumping from an old stale position.
        """
        self.prev_x = None
        self.prev_y = None