from .base_agent import BaseAgent
from thefuzz import fuzz

class ReconciliationAgent(BaseAgent):
    """
    An AI agent for reconciling transactions.
    """

    def __init__(self, similarity_threshold=80):
        self.similarity_threshold = similarity_threshold

    def process(self, data):
        """
        Reconcile the given data using fuzzy matching.

        :param data: A dictionary containing two lists of transactions to reconcile.
                     Example: {'source1': [{'id': 1, 'description': 'Coffee', 'amount': 5.00}],
                               'source2': [{'id': 2, 'description': 'Coffee Shop', 'amount': 5.00}]}
        :return: A list of matched transaction pairs, with the match score.
        """
        source1_transactions = data.get('source1', [])
        source2_transactions = data.get('source2', [])
        matched_pairs = []

        # Create a copy of the second list to be able to remove items from it
        remaining_source2 = list(source2_transactions)

        for t1 in source1_transactions:
            best_match = None
            highest_score = -1

            for t2 in remaining_source2:
                if t1.get('amount') == t2.get('amount'):
                    description1 = t1.get('description', '')
                    description2 = t2.get('description', '')

                    score = fuzz.ratio(description1.lower(), description2.lower())

                    if score >= self.similarity_threshold and score > highest_score:
                        highest_score = score
                        best_match = t2

            if best_match:
                matched_pairs.append((t1, best_match, highest_score))
                remaining_source2.remove(best_match)

        return matched_pairs
