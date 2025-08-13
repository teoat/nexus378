import json
from agents.reconciliation_agent import create_reconciliation_agent
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(message):
    """
    Main entry point for the AI service worker.
    """
    data = json.loads(message)
    agent = create_reconciliation_agent()
    result = agent.invoke(data)
    print(f"Agent finished with result: {result}")


if __name__ == "__main__":
    # This is for local testing only. In production, the consumer will call the main function.
    test_message = {
        "job_id": "test-job-123",
        "case_id": "test-case-456",
        "file_id": "test-file-789",
        "mapping_id": "test-mapping-abc",
        "scope": "all",
        "scope_value": None,
        "requested_by": "test-user-xyz",
    }
    main(json.dumps(test_message))
