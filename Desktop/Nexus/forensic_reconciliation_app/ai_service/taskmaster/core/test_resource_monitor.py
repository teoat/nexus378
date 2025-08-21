import asyncio
import unittest
from unittest.mock import patch
import psutil

from .resource_monitor import ResourceMonitor, SystemMetrics

class TestResourceMonitor(unittest.TestCase):

    def setUp(self):
        self.monitor = ResourceMonitor()

    @patch('psutil.cpu_percent', return_value=50.0)
    @patch('psutil.virtual_memory', return_value=psutil._common.svmem(total=100, available=50, percent=50, used=50, free=50))
    @patch('psutil.disk_usage', return_value=psutil._common.sdiskusage(total=100, used=50, free=50, percent=50))
    @patch('psutil.net_connections', return_value=[])
    def test_monitoring(self, mock_net, mock_disk, mock_mem, mock_cpu):
        async def run_test():
            await self.monitor.start_monitoring()
            await asyncio.sleep(0.1) # allow some time for metrics to be collected

            summary = self.monitor.get_system_summary()
            self.assertEqual(summary['status'], 'monitoring')
            self.assertEqual(summary['current']['cpu_percent'], 50.0)
            self.assertEqual(summary['current']['memory_percent'], 50.0)
            self.assertEqual(summary['current']['disk_percent'], 50.0)

            health = self.monitor.get_health()
            self.assertTrue(health['healthy'])

            await self.monitor.stop_monitoring()

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
