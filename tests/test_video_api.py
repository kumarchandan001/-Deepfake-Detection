import unittest
import os
import sys
from fastapi.testclient import TestClient
# Insert path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app import app

class TestVideoFastAPIRoutes(unittest.TestCase):
    """
    Validates ASGI video routing mappings using FastAPI TestClient.
    """
    def setUp(self):
        self.client = TestClient(app)

    def test_video_invalid_format_upload(self):
        """
        Routes should reject unsupported video format uploads cleanly.
        """
        # Upload a simulated text file instead of mp4/avi
        response = self.client.post(
            "/api/v1/forensics/video/analyze",
            files={"file": ("test.txt", b"dummy video content", "text/plain")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported format", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
