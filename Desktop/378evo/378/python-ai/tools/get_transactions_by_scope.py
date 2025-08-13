from langchain.tools import tool
from sqlalchemy import create_engine, text
import os


@tool
def get_transactions_by_scope(
    scope: str, scope_value: str, case_id: str
) -> list:
    """
    Fetches transactions from the database based on a given scope (e.g., month, trimester).
    """
    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.connect() as connection:
        # This is a simplified example. In a real-world scenario, you would have
        # more robust logic to handle different scopes and prevent SQL injection.
        if scope == "month":
            query = text(
                "SELECT * FROM transactions WHERE case_id = :case_id AND EXTRACT(MONTH FROM transaction_date) = :scope_value"
            )
        elif scope == "trimester":
            # This logic would need to be more complex to handle trimesters
            query = text(
                "SELECT * FROM transactions WHERE case_id = :case_id AND EXTRACT(QUARTER FROM transaction_date) = :scope_value"
            )
        else:
            query = text("SELECT * FROM transactions WHERE case_id = :case_id")

        result = connection.execute(
            query, {"case_id": case_id, "scope_value": scope_value}
        )
        return [dict(row) for row in result]
