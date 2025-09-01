import time
import unittest
from unittest.mock import MagicMock

    AutoScaler, ScalingDecision)
    Agent

class TestAutoScaler(unittest.TestCase):

    def setUp(self):

            "MIN_AGENTS": 2,
            "MAX_AGENTS": 5,
            "TASKS_PER_AGENT_THRESHOLD": 3,
            "IDLE_AGENT_PERCENT_THRESHOLD": 0.6,  # 60%
            "COOLDOWN_PERIOD_S": 10,  # Short cooldown for testing
        }
        self.autoscaler = AutoScaler(self.mock_mcp_server, self.config)

    def test_decision_scale_up(self):

            "task_status": {"pending": 15, "in_progress": 3},
            "agents": {"total_registered": 3},
        }

        decision = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision, ScalingDecision.SCALE_UP)

    def test_decision_scale_down(self):

            "task_status": {"pending": 0, "in_progress": 1},
            "agents": {"total_registered": 5},
        }

        decision = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision, ScalingDecision.SCALE_DOWN)

    def test_decision_hold_due_to_max_agents(self):

            "task_status": {"pending": 20, "in_progress": 5},
            "agents": {"total_registered": 5},  # MAX_AGENTS is 5
        }

        decision = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision, ScalingDecision.HOLD)

    def test_decision_hold_due_to_min_agents(self):

            "task_status": {"pending": 0, "in_progress": 0},
            "agents": {"total_registered": 2},  # MIN_AGENTS is 2
        }

        decision = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision, ScalingDecision.HOLD)

    def test_decision_hold_due_to_stable_load(self):

            "task_status": {"pending": 5, "in_progress": 3},
            "agents": {"total_registered": 3},  # 5/3 < 3
        }

        decision = self.autoscaler.make_scaling_decision()
        self.assertEqual(decision, ScalingDecision.HOLD)

    def test_cooldown_period(self):

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
