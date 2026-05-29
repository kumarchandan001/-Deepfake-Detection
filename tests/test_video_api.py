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
        # Register a test tenant with Pro plan to satisfy QuotaEnforcementMiddleware checks
        from enterprise.saas.subscription_manager import SubscriptionManager
        import asyncio
        
        async def setup_sub():
            manager = SubscriptionManager()
            sub = await manager.get_subscription("test_video_tenant")
            sub.plan_key = "pro"
            sub.status = "active"
            await manager.update_subscription_cache(sub)
            
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If an event loop is already running in this thread, run the task using a future/task
                import nest_asyncio
                nest_asyncio.apply()
            asyncio.run(setup_sub())
        except Exception:
            # Fallback for when loop/async environment is already running or initialized
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(setup_sub())
            except Exception:
                pass

    def test_video_invalid_format_upload(self):
        """
        Routes should reject unsupported video format uploads cleanly.
        """
        # Upload a simulated text file instead of mp4/avi
        response = self.client.post(
            "/api/v1/forensics/video/analyze",
            files={"file": ("test.txt", b"dummy video content", "text/plain")},
            headers={"X-Tenant-ID": "test_video_tenant"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported format", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
