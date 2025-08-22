import unittest
from .reconciliation_agent import ReconciliationAgent

class TestReconciliationAgent(unittest.TestCase):

    def setUp(self):
        self.agent = ReconciliationAgent(similarity_threshold=80)

    def test_simple_reconciliation(self):
        source1 = [
            {'id': 1, 'description': 'Starbucks Coffee', 'amount': 5.00},
            {'id': 2, 'description': 'McDonalds', 'amount': 12.50},
            {'id': 3, 'description': 'Gas Station', 'amount': 45.00},
        ]
        source2 = [
            {'id': 101, 'description': 'Starbucks', 'amount': 5.00},
            {'id': 102, 'description': 'McD', 'amount': 12.50},
            {'id': 103, 'description': 'Shell Gas', 'amount': 45.00},
            {'id': 104, 'description': 'Burger King', 'amount': 15.00},
        ]

        data = {'source1': source1, 'source2': source2}
        matched_pairs = self.agent.process(data)

        self.assertEqual(len(matched_pairs), 3)

        # Check the first matched pair
        self.assertEqual(matched_pairs[0][0]['id'], 1)
        self.assertEqual(matched_pairs[0][1]['id'], 101)

        # Check the second matched pair
        self.assertEqual(matched_pairs[1][0]['id'], 2)
        self.assertEqual(matched_pairs[1][1]['id'], 102)

        # Check the third matched pair
        self.assertEqual(matched_pairs[2][0]['id'], 3)
        self.assertEqual(matched_pairs[2][1]['id'], 103)

    def test_no_matches(self):
        source1 = [
            {'id': 1, 'description': 'A', 'amount': 1.00},
        ]
        source2 = [
            {'id': 101, 'description': 'B', 'amount': 2.00},
        ]

        data = {'source1': source1, 'source2': source2}
        matched_pairs = self.agent.process(data)
        self.assertEqual(len(matched_pairs), 0)

    def test_duplicate_amounts_best_match(self):
        source1 = [
            {'id': 1, 'description': 'Apple Store', 'amount': 999.00},
        ]
        source2 = [
            {'id': 101, 'description': 'Apple Inc.', 'amount': 999.00},
            {'id': 102, 'description': 'Microsoft Store', 'amount': 999.00},
        ]

        data = {'source1': source1, 'source2': source2}
        matched_pairs = self.agent.process(data)

        self.assertEqual(len(matched_pairs), 1)
        self.assertEqual(matched_pairs[0][0]['id'], 1)
        self.assertEqual(matched_pairs[0][1]['id'], 101) # Should match Apple Inc. not Microsoft

if __name__ == '__main__':
    unittest.main()
