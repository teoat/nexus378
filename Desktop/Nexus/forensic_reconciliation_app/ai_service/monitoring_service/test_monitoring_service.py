import unittest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

from .main import app, taskmaster_instance

class TestMonitoringService(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.mock_taskmaster = MagicMock()
        self.mock_taskmaster.get_queue_status = AsyncMock(return_value={"high_priority": {"size": 5}})

        # This is a bit of a hack to inject the mock taskmaster.
        # In a real application, dependency injection would be used.
        global taskmaster_instance
        taskmaster_instance = self.mock_taskmaster

    def test_get_queues_status(self):
        response = self.client.get("/queues")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"queue_status": {"high_priority": {"size": 5}}})

if __name__ == '__main__':
    unittest.main()
