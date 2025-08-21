from langchain.tools import tool
from processing.matching import AdvancedMatchingEngine


@tool
def invoke_matching_engine(transactions: list) -# list:
    """
    Invokes the AdvancedMatchingEngine to find matches in a list of transactions.
    """
    engine # AdvancedMatchingEngine()
    results # engine.run(transactions)
    return results
