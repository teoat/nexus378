import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from .auto_scaler import AutoScaler
from .taskmaster import Taskmaster, TaskmasterConfig

class TestAutoScaler(unittest.TestCase):

    def setUp(self):
        self.config = TaskmasterConfig()
        self.taskmaster = Taskmaster(self.config)
        self.auto_scaler = AutoScaler(self.config, taskmaster=self.taskmaster)
        self.auto_scaler._scale_up_agents = AsyncMock()
        self.auto_scaler._scale_down_agents = AsyncMock()

    @patch('__main__.AutoScaler._collect_workload_metrics')
    def test_scale_up(self, mock_metrics):
        async def run_test():
            # Simulate high load
            mock_metrics.return_value = {
                'cpu_utilization': 0.9,
                'memory_utilization': 0.85,
                'queue_length': 30,
                'response_time': 6.0
            }
            self.taskmaster.active_agents = {'agent1': MagicMock()}

            await self.auto_scaler._evaluate_scaling_needs()

            self.auto_scaler._scale_up_agents.assert_called_once()

        asyncio.run(run_test())

    @patch('__main__.AutoScaler._collect_workload_metrics')
    def test_scale_down(self, mock_metrics):
        async def run_test():
            # Simulate low load
            mock_metrics.return_value = {
                'cpu_utilization': 0.1,
                'memory_utilization': 0.15,
                'queue_length': 1,
                'response_time': 0.5
            }
            self.taskmaster.active_agents = {f'agent{i}': MagicMock() for i in range(10)}

            await self.auto_scaler._evaluate_scaling_needs()

            self.auto_scaler._scale_down_agents.assert_called_once()

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
