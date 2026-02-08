from collections import deque
import numpy as np

class GazeTracker:
    """
    Smoothing and processing logic for gaze tracking.
    Uses a moving average filter to stabilize the gaze point.
    """
    def __init__(self, buffer_size=10):
        """
        Args:
            buffer_size (int): Number of frames to keep for smoothing average.
        """
        self.gaze_buffer = deque(maxlen=buffer_size)

    def smooth_gaze(self, screen_point):
        """
        Applies a moving average filter to the gaze point to reduce jitter.

        Args:
            screen_point (tuple): Raw (x, y) screen coordinates.

        Returns:
            tuple: Smoothed (x, y) coordinates, or None if input is None.
        """
        if screen_point is None:
            return None
            
        self.gaze_buffer.append(screen_point)
        
        # Calculate averge of the buffer
        avg_x = sum(p[0] for p in self.gaze_buffer) / len(self.gaze_buffer)
        avg_y = sum(p[1] for p in self.gaze_buffer) / len(self.gaze_buffer)
        
        return (int(avg_x), int(avg_y))
