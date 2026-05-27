import unittest
import os
import sys
from fastapi.testclient import TestClient
# Insert path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app import app

class TestFastAPIRoutes(unittest.TestCase):
    """
    Validates ASGI entrypoint routing mappings using TestClient.
    """
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        """
        Health check route should return HEALTHY status.
        """
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "HEALTHY")

    def test_invalid_mime_type_upload(self):
        """
        Routes should reject unsupported format uploads cleanly.
        """
        # Upload a simulated text file
        response = self.client.post(
            "/api/v1/forensics/analyze",
            files={"file": ("test.txt", b"dummy content", "text/plain")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported format", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
