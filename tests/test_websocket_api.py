import unittest
import os
import sys
import numpy as np
import cv2
from fastapi.testclient import TestClient

# Ensure workspace path imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app

class TestWebSocketAPI(unittest.TestCase):
    """
    Validates streaming binary WebSocket frame ingestion and output JSON schemas.
    """
    def setUp(self):
        self.client = TestClient(app)
        
        # Create a synthetic 100x100 RGB image (numpy matrix) and encode as JPEG bytes
        synthetic_img = np.zeros((100, 100, 3), dtype=np.uint8)
        # Draw a central rectangle to simulate facial texture structure
        cv2.rectangle(synthetic_img, (30, 30), (70, 70), (255, 255, 255), -1)
        ret, jpeg_buffer = cv2.imencode(".jpg", synthetic_img)
        self.assertTrue(ret)
        self.raw_image_bytes = jpeg_buffer.tobytes()

    def test_websocket_stream_processing(self):
        """
        WebSocket stream should ingest binary frames and broadcast correct JSON predictions.
        """
        # Connect to FastAPI WebSocket stream endpoint
        with self.client.websocket_connect("/api/v1/forensics/realtime/stream") as websocket:
            # Stream a mock binary frame
            websocket.send_bytes(self.raw_image_bytes)
            
            # Await broadcast json message response
            response = websocket.receive_json()
            
            # Assert response payload matches Phase 5 schema standards
            self.assertTrue(response["success"])
            self.assertIn("prediction", response)
            self.assertIn("confidence", response)
            self.assertIn("processing_time", response)
            self.assertIn("face_detected", response)

if __name__ == "__main__":
    unittest.main()
