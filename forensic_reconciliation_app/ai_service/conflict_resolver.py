import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConflictResolver:
    def __init__(self):
        logging.info("ConflictResolver initialized.")

    def resolve(self, incoming_data: Dict[str, Any], existing_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolves conflicts between incoming data and existing data.
        For simplicity, this implementation uses a 'last-write wins' strategy based on timestamp.
        If incoming_data has a later timestamp, it overrides existing_data.
        If no existing_data, incoming_data is returned as is.
        """
        if not existing_data:
            logging.info(f"No existing data for ID {incoming_data.get('id', 'N/A')}. Incoming data accepted.")
            return incoming_data

        incoming_id = incoming_data.get('id')
        existing_id = existing_data.get('id')

        if incoming_id != existing_id:
            logging.warning(f"Attempting to resolve conflict for different IDs: Incoming {incoming_id}, Existing {existing_id}. This should not happen if resolution is by ID.")
            # In a real system, this might indicate a logic error or require different handling
            return incoming_data # Default to incoming if IDs don't match (should be handled upstream)

        incoming_timestamp_str = incoming_data.get('timestamp')
        existing_timestamp_str = existing_data.get('timestamp')

        # Basic timestamp comparison. In a real system, convert to datetime objects for robust comparison.
        if incoming_timestamp_str and existing_timestamp_str:
            if incoming_timestamp_str > existing_timestamp_str:
                logging.info(f"Conflict for ID {incoming_id}: Incoming data is newer. Accepting incoming.")
                return incoming_data
            elif incoming_timestamp_str < existing_timestamp_str:
                logging.info(f"Conflict for ID {incoming_id}: Existing data is newer. Keeping existing.")
                return existing_data
            else:
                logging.info(f"Conflict for ID {incoming_id}: Timestamps are identical. Defaulting to incoming data.")
                return incoming_data # Timestamps are same, default to incoming
        else:
            logging.warning(f"Conflict for ID {incoming_id}: Missing timestamp in one or both datasets. Defaulting to incoming data.")
            return incoming_data # If timestamps are missing, default to incoming

if __name__ == "__main__":
    resolver = ConflictResolver()

    # Test cases
    existing_data_1 = {
        "id": "event-1",
        "timestamp": "2025-08-25T10:00:00Z",
        "source_system": "sys_a",
        "event_type": "login",
        "payload": {"user": "john"}
    }

    incoming_data_1_newer = {
        "id": "event-1",
        "timestamp": "2025-08-25T10:05:00Z",
        "source_system": "sys_b",
        "event_type": "logout",
        "payload": {"user": "john", "duration": 300}
    }

    incoming_data_1_older = {
        "id": "event-1",
        "timestamp": "2025-08-25T09:55:00Z",
        "source_system": "sys_c",
        "event_type": "activity",
        "payload": {"user": "john", "action": "view"}
    }

    incoming_data_2_new = {
        "id": "event-2",
        "timestamp": "2025-08-25T11:00:00Z",
        "source_system": "sys_d",
        "event_type": "purchase",
        "payload": {"item": "book"}
    }

    print("\n--- Test Case 1: Incoming is newer ---")
    resolved = resolver.resolve(incoming_data_1_newer, existing_data_1)
    print(f"Resolved data: {resolved}")

    print("\n--- Test Case 2: Incoming is older ---")
    resolved = resolver.resolve(incoming_data_1_older, existing_data_1)
    print(f"Resolved data: {resolved}")

    print("\n--- Test Case 3: No existing data ---")
    resolved = resolver.resolve(incoming_data_2_new, None)
    print(f"Resolved data: {resolved}")

    print("\n--- Test Case 4: Timestamps are identical ---")
    identical_timestamp_incoming = {
        "id": "event-1",
        "timestamp": "2025-08-25T10:00:00Z",
        "source_system": "sys_e",
        "event_type": "update",
        "payload": {"status": "processed"}
    }
    resolved = resolver.resolve(identical_timestamp_incoming, existing_data_1)
    print(f"Resolved data: {resolved}")
