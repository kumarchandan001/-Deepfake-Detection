import queue
import threading
import numpy as np
from typing import Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("frame_queue")

class ThreadSafeFrameQueue:
    """
    A thread-safe, size-bounded frame buffer queue designed to manage
    high-speed real-time video streams. Drops older frames automatically
    if processing latency lags behind capture frequency.
    """
    def __init__(self, maxsize: int = 5):
        self.maxsize = maxsize
        self.queue = queue.Queue(maxsize=maxsize)
        self.lock = threading.Lock()
        self.dropped_frames = 0
        logger.info(f"ThreadSafeFrameQueue initialized. Max Capacity: {maxsize}")

    def put(self, frame: np.ndarray) -> None:
        """
        Pushes a new frame onto the queue. If queue is full, discards the oldest
        frame to prevent temporal drift.
        """
        with self.lock:
            if self.queue.full():
                try:
                    self.queue.get_nowait() # Remove oldest frame to clear slot
                    self.dropped_frames += 1
                except queue.Empty:
                    pass
            self.queue.put(frame)

    def get(self, block: bool = True, timeout: Optional[float] = None) -> Optional[np.ndarray]:
        """
        Retrieves next frame from queue.
        """
        try:
            return self.queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def get_dropped_count(self) -> int:
        with self.lock:
            return self.dropped_frames

    def size(self) -> int:
        return self.queue.qsize()

    def clear(self) -> None:
        with self.lock:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except queue.Empty:
                    break
            self.dropped_frames = 0
