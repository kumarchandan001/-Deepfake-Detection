import time
from collections import deque

class FPSMonitor:
    """
    Measures frame processing rates (Frames Per Second) dynamically 
    using a sliding temporal window of target length.
    """
    def __init__(self, window_size: int = 30):
        self.timestamps = deque(maxlen=window_size)

    def tick(self) -> None:
        """
        Registers a new frame processing event.
        """
        self.timestamps.append(time.time())

    def get_fps(self) -> float:
        """
        Returns average FPS computed over the window.
        """
        if len(self.timestamps) < 2:
            return 0.0
            
        duration = self.timestamps[-1] - self.timestamps[0]
        if duration <= 0:
            return 0.0
            
        return len(self.timestamps) / duration
