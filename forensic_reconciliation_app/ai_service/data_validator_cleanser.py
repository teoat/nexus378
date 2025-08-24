import json
import logging
from typing import Dict, Any, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataValidatorCleanser:
    def __init__(self):
        # Define a simple expected schema for forensic data
        # In a real application, this would be much more complex and potentially loaded from a config.
        self.expected_schema = {
            "id": {"type": "string", "required": True},
            "timestamp": {"type": "string", "required": True, "format": "datetime"},
            "source_system": {"type": "string", "required": True},
            "event_type": {"type": "string", "required": True},
            "payload": {"type": "object", "required": True},
            "status": {"type": "string", "required": False, "default": "raw"}
        }

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates the incoming data against the defined schema.
        Returns (True, "") if valid, otherwise (False, "error_message").
        """
        if not isinstance(data, dict):
            return False, "Data is not a dictionary."

        for field, props in self.expected_schema.items():
            is_required = props.get("required", False)
            field_type = props.get("type")

            if is_required and field not in data:
                return False, f"Missing required field: {field}"

            if field in data:
                # Basic type checking
                if field_type == "string" and not isinstance(data[field], str):
                    return False, f"Field {field} expected type string, got {type(data[field]).__name__}"
                elif field_type == "object" and not isinstance(data[field], dict):
                    return False, f"Field {field} expected type object, got {type(data[field]).__name__}"
                # Add more type checks as needed (e.g., int, float, bool)

                # Specific format checks (e.g., datetime)
                if field_type == "string" and props.get("format") == "datetime":
                    # A more robust datetime validation would use a library like dateutil or pendulum
                    try:
                        # Simple check for now: ensure it's a non-empty string
                        if not data[field]:
                            return False, f"Field {field} (datetime) cannot be empty."
                    except Exception:
                        return False, f"Field {field} is not a valid datetime string."

        return True, ""

    def cleanse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleanses the incoming data based on predefined rules.
        Returns the cleansed data.
        """
        cleansed_data = data.copy()

        for field, props in self.expected_schema.items():
            if field in cleansed_data:
                # Strip whitespace from strings
                if props.get("type") == "string" and isinstance(cleansed_data[field], str):
                    cleansed_data[field] = cleansed_data[field].strip()

            # Apply defaults for missing non-required fields
            elif field not in cleansed_data and "default" in props:
                cleansed_data[field] = props["default"]

        # Example of a more complex cleansing rule: ensure payload is a dict
        if "payload" in cleansed_data and not isinstance(cleansed_data["payload"], dict):
            logging.warning(f"Payload for ID {cleansed_data.get('id', 'N/A')} is not a dictionary. Attempting to convert.")
            try:
                # If payload is a string, try to parse it as JSON
                if isinstance(cleansed_data["payload"], str):
                    cleansed_data["payload"] = json.loads(cleansed_data["payload"])
                else:
                    # If it's something else, just make it an empty dict to avoid errors downstream
                    cleansed_data["payload"] = {}
            except json.JSONDecodeError:
                logging.error(f"Could not parse payload string as JSON for ID {cleansed_data.get('id', 'N/A')}. Setting to empty dict.")
                cleansed_data["payload"] = {}
            except Exception as e:
                logging.error(f"Unexpected error during payload cleansing for ID {cleansed_data.get('id', 'N/A')}: {e}. Setting to empty dict.")
                cleansed_data["payload"] = {}

        return cleansed_data

if __name__ == "__main__":
    validator_cleanser = DataValidatorCleanser()

    # Test cases
    valid_data = {
        "id": "event-123",
        "timestamp": "2025-08-25T10:00:00Z",
        "source_system": "sys_a",
        "event_type": "login_attempt",
        "payload": {"user_id": "user1", "status": "success"}
    }

    invalid_missing_field = {
        "id": "event-124",
        "timestamp": "2025-08-25T10:01:00Z",
        "source_system": "sys_b",
        "payload": {"user_id": "user2"}
    }

    invalid_type = {
        "id": "event-125",
        "timestamp": "2025-08-25T10:02:00Z",
        "source_system": "sys_c",
        "event_type": 123, # Incorrect type
        "payload": {"user_id": "user3"}
    }

    data_to_cleanse = {
        "id": "event-126 ", # Trailing space
        "timestamp": " 2025-08-25T10:03:00Z ",
        "source_system": "sys_d",
        "event_type": " logout ",
        "payload": "{\"session_id\": \"abc\"}" # Payload as string
    }

    print("\n--- Testing Validation ---")
    is_valid, msg = validator_cleanser.validate(valid_data)
    print(f"Valid data: {is_valid}, {msg}")

    is_valid, msg = validator_cleanser.validate(invalid_missing_field)
    print(f"Invalid (missing field) data: {is_valid}, {msg}")

    is_valid, msg = validator_cleanser.validate(invalid_type)
    print(f"Invalid (type) data: {is_valid}, {msg}")

    print("\n--- Testing Cleansing ---")
    cleansed_data = validator_cleanser.cleansed(data_to_cleanse)
    print(f"Original: {data_to_cleanse}")
    print(f"Cleansed: {cleansed_data}")

    # Test with a payload that cannot be parsed
    data_with_bad_payload = {
        "id": "event-127",
        "timestamp": "2025-08-25T10:04:00Z",
        "source_system": "sys_e",
        "event_type": "error",
        "payload": "not a json string"
    }
    cleansed_bad_payload = validator_cleanser.cleansed(data_with_bad_payload)
    print(f"\nCleansed (bad payload): {cleansed_bad_payload}")
