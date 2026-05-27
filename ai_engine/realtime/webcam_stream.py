import cv2
import threading
import time
from typing import Optional
from ai_engine.realtime.frame_queue import ThreadSafeFrameQueue
from ai_engine.utils.logger import setup_logger

logger = setup_logger("webcam_stream")

class MultithreadedWebcamStream:
    """
    Spawns a lightweight background thread to continually query camera frames,
    pushing them into a ThreadSafeFrameQueue to keep ingestion latency at exactly zero.
    """
    def __init__(self, src: int = 0, queue_size: int = 5):
        self.src = src
        self.cap = cv2.VideoCapture(src)
        self.frame_queue = ThreadSafeFrameQueue(maxsize=queue_size)
        self.stopped = False
        self.thread: Optional[threading.Thread] = None

        if not self.cap.isOpened():
            logger.error(f"Failed to open webcam hardware stream at source index: {src}")
            raise IOError(f"Camera index {src} could not be initialized.")
        logger.info(f"Webcam stream initialized on index {src}.")

    def start(self) -> "MultithreadedWebcamStream":
        """
        Starts frame reading loop in background thread.
        """
        self.stopped = False
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.daemon = True # Daemon threads shut down automatically with parent app
        self.thread.start()
        logger.info("Background webcam stream thread spawned.")
        return self

    def _update(self) -> None:
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Failed to grab next webcam frame. Re-initiating descriptor capture...")
                time.sleep(0.01)
                continue
            self.frame_queue.put(frame)

    def read(self) -> Optional[tuple]:
        """
        Retrieves the latest available frame from queue.
        """
        return self.frame_queue.get(block=False)

    def stop(self) -> None:
        """
        Stops loop and releases camera descriptors.
        """
        self.stopped = True
        if self.thread is not None:
            self.thread.join(timeout=1.0)
        self.cap.release()
        logger.info("Webcam stream capture stopped cleanly.")
