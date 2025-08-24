import datetime
import json

LOG_FILE = "chain_of_custody.log"


def log_event(item_id: str, event_description: str, user_id: str):
    event = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "item_id": item_id,
        "event_description": event_description,
        "user_id": user_id,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")


def get_history(item_id: str) -> list:
    """Retrieves the history of events for an item."""
    history = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                event = json.loads(line)
                if event["item_id"] == item_id:
                    history.append(event)
    except FileNotFoundError:
        pass  # No history yet
    return history
