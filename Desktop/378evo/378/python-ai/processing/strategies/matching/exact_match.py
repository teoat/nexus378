class ExactMatchStrategy:
    def find_matches(self, transactions):
        """
        Matches transactions with the exact same amount and description.
        """
        print("Running exact match strategy...")
        matches = []
        for i in range(len(transactions)):
            for j in range(i + 1, len(transactions)):
                if (
                    transactions[i]["amount"] == transactions[j]["amount"]
                    and transactions[i]["description"]
                    == transactions[j]["description"]
                ):
                    matches.append((transactions[i], transactions[j]))
        return matches
