from thefuzz import fuzz


class FuzzyMatchStrategy:
    def find_matches(self, transactions, threshold=80):
        """
        Matches transactions with similar descriptions.
        """
        print("Running fuzzy match strategy...")
        matches = []
        for i in range(len(transactions)):
            for j in range(i + 1, len(transactions)):
                if (
                    fuzz.ratio(
                        transactions[i]["description"],
                        transactions[j]["description"],
                    )
                    > threshold
                ):
                    matches.append((transactions[i], transactions[j]))
        return matches
