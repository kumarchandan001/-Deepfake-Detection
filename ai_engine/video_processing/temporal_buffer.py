import numpy as np
from typing import List

class TemporalBuffer:
    """
    Manages sequence queues, aligning sliding temporal windows for 
    high-throughput streaming or batch sequence parsing.
    """
    def __init__(self, buffer_size: int = 16):
        self.buffer_size = buffer_size
        self.queue: List[np.ndarray] = []

    def push(self, frame: np.ndarray) -> None:
        """
        Pushes a new frame into the sliding queue buffer.
        """
        self.queue.append(frame)
        if len(self.queue) > self.buffer_size:
            self.queue.pop(0) # Maintain sliding threshold length

    def is_full(self) -> bool:
        """
        Returns True if queue satisfies sliding window length parameters.
        """
        return len(self.queue) == self.buffer_size

    def get_sequence(self) -> List[np.ndarray]:
        """
        Returns current buffer state.
        """
        return list(self.queue)

    def clear(self) -> None:
        """
        Resets active queue state.
        """
        self.queue.clear()
