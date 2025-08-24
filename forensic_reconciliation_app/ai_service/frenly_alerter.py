import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FrenlyAlerter:
    def __init__(self):
        logging.info("FrenlyAlerter initialized.")

    def send_alert(self, message: str, severity: str = "info", event_id: str = "N/A"):
        """
        Sends an alert message with a specified severity.
        In a real system, this would integrate with external alerting tools (e.g., PagerDuty, Slack, Email).
        For now, it logs the alert with appropriate severity.
        """
        alert_message = f"[FRENLY ALERT - {severity.upper()}] Event ID: {event_id} - {message}"

        if severity.lower() == "critical":
            logging.critical(alert_message)
        elif severity.lower() == "error":
            logging.error(alert_message)
        elif severity.lower() == "warning":
            logging.warning(alert_message)
        else:
            logging.info(alert_message) # Default to info

        logging.info(f"Alert sent: {alert_message}")

if __name__ == "__main__":
    alerter = FrenlyAlerter()

    print("\n--- Testing Alerter ---")
    alerter.send_alert("System started successfully.", "info")
    alerter.send_alert("High volume of pending reconciliations.", "warning", "batch-123")
    alerter.send_alert("Database connection lost to primary replica!", "critical", "db-conn-001")
    alerter.send_alert("Anomaly detected in transaction amount for event X.", "error", "event-X")
