import os

from .chain_of_custody import LOG_FILE
from .main import app

client = TestClient(app)


def test_log_and_get_history():
    """test_log_and_get_history function."""
    item_id = "test_item_123"

    # Clean up log file before test
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    # Log some events
    client.post(
        "/log_event",
        json={"item_id": item_id, "event_description": "Created", "user_id": "user1"},
    )
    client.post(
        "/log_event",
        json={"item_id": item_id, "event_description": "Viewed", "user_id": "user2"},
    )

    # Get history
    response = client.post("/get_history", json={"item_id": item_id})
    assert response.status_code == 200
    history = response.json()["history"]

    assert len(history) == 2
    assert history[0]["event_description"] == "Created"
    assert history[1]["user_id"] == "user2"

    # Clean up log file after test
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
