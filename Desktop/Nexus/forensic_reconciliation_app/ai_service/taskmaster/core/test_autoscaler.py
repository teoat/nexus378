import time
import unittest
from unittest.mock import MagicMock

from Desktop.Nexus.forensic_reconciliation_app.ai_service.taskmaster.core.autoscaler import (
    AutoScaler,
    ScalingDecision,
)
from Desktop.Nexus.forensic_reconciliation_app.ai_service.taskmaster.core.mcp_server import (
    Agent,
)


class TestAutoScaler(unittest.TestCase):

    def setUp(self):
        """Set up a mock mcp_server and a default autoscaler config for each test."""
        self.mock_mcp_server = MagicMock()
        self.config = {
            "MIN_AGENTS": 2,
            "MAX_AGENTS": 5,
            "TASKS_PER_AGENT_THRESHOLD": 3,
            "IDLE_AGENT_PERCENT_THRESHOLD": 0.6,  # 60%
            "COOLDOWN_PERIOD_S": 10,  # Short cooldown for testing
        }
        self.autoscaler = AutoScaler(self.mock_mcp_server, self.config)

    def test_decision_scale_up(self):
        """Test that the scaler decides to SCALE_UP when load is high."""
        # Simulate high load: 15 pending tasks, 3 agents (5 tasks/agent > threshold of 3)
        self.mock_mcp_server.get_system_status.return_value = {
            "task_status": {"pending": 15, "in_progress": 3},
            "agents": {"total_registered": 3},
        }

        decision = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision, ScalingDecision.SCALE_UP)

    def test_decision_scale_down(self):
        """Test that the scaler decides to SCALE_DOWN when many agents are idle."""
        # Simulate low load: 0 pending tasks, 5 agents, 1 busy (4 idle = 80% > threshold of 60%)
        self.mock_mcp_server.get_system_status.return_value = {
            "task_status": {"pending": 0, "in_progress": 1},
            "agents": {"total_registered": 5},
        }

        decision = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision, ScalingDecision.SCALE_DOWN)

    def test_decision_hold_due_to_max_agents(self):
        """Test HOLD decision when load is high but max agents are reached."""
        # High load, but already at max agents
        self.mock_mcp_server.get_system_status.return_value = {
            "task_status": {"pending": 20, "in_progress": 5},
            "agents": {"total_registered": 5},  # MAX_AGENTS is 5
        }

        decision = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision, ScalingDecision.HOLD)

    def test_decision_hold_due_to_min_agents(self):
        """Test HOLD decision when agents are idle but min agents are reached."""
        # Idle agents, but already at min agents
        self.mock_mcp_server.get_system_status.return_value = {
            "task_status": {"pending": 0, "in_progress": 0},
            "agents": {"total_registered": 2},  # MIN_AGENTS is 2
        }

        decision = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision, ScalingDecision.HOLD)

    def test_decision_hold_due_to_stable_load(self):
        """Test HOLD decision when the system load is stable."""
        # Load is below the scale-up threshold
        self.mock_mcp_server.get_system_status.return_value = {
            "task_status": {"pending": 5, "in_progress": 3},
            "agents": {"total_registered": 3},  # 5/3 < 3
        }

        decision = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision, ScalingDecision.HOLD)

    def test_cooldown_period(self):
        """Test that the cooldown period prevents rapid scaling."""
        # Trigger a scale up
        self.mock_mcp_server.get_system_status.return_value = {
            "task_status": {"pending": 15, "in_progress": 3},
            "agents": {"total_registered": 3},
        }
        decision1 = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision1, ScalingDecision.SCALE_UP)

        # Immediately try to scale up again
        # The decision should be HOLD because we are in the cooldown period
        decision2 = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision2, ScalingDecision.HOLD)

        # Wait for cooldown to expire
        time.sleep(self.config["COOLDOWN_PERIOD_S"])

        # Try to scale up again, it should now be allowed
        decision3 = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision3, ScalingDecision.SCALE_UP)


if __name__ == "__main__":
    unittest.main()
