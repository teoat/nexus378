import logging
from collections import Counter

from .frenly_data_storage import FrenlyDataStorage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FrenlyReporter:
    def __init__(self):
        self.data_storage = FrenlyDataStorage()
        try:
            self.data_storage.connect()
        except Exception as e:
            logging.error(f"Failed to connect to database for reporting: {e}")
            self.data_storage = None # Ensure it's None if connection fails

    def get_reconciliation_summary(self) -> dict:
        """
        Generates a summary of reconciliation statuses.
        """
        if not self.data_storage or not self.data_storage.conn:
            logging.error("Database connection not available for reporting.")
            return {"error": "Database not connected"}

        try:
            with self.data_storage.conn.cursor() as cur:
                cur.execute("SELECT reconciliation_status FROM reconciled_forensic_data;")
                statuses = [row[0] for row in cur.fetchall()]
            
            summary = Counter(statuses)
            return dict(summary)
        except Exception as e:
            logging.error(f"Error retrieving reconciliation summary: {e}")
            return {"error": str(e)}

    def get_anomalous_events(self, limit: int = 10) -> list:
        """
        Retrieves a list of events marked as 'anomaly'.
        """
        if not self.data_storage or not self.data_storage.conn:
            logging.error("Database connection not available for reporting.")
            return []

        try:
            with self.data_storage.conn.cursor() as cur:
                cur.execute("SELECT id, timestamp, source_system, event_type, reconciliation_status FROM reconciled_forensic_data WHERE reconciliation_status = 'anomaly' ORDER BY timestamp DESC LIMIT %s;", (limit,))
                anomalies = []
                for row in cur.fetchall():
                    anomalies.append({
                        "id": row[0],
                        "timestamp": row[1].isoformat() if row[1] else None,
                        "source_system": row[2],
                        "event_type": row[3],
                        "reconciliation_status": row[4]
                    })
                return anomalies
        except Exception as e:
            logging.error(f"Error retrieving anomalous events: {e}")
            return []

    def generate_report(self):
        """
        Generates and prints a comprehensive text-based report.
        """
        logging.info("\n--- FRENLY Reconciliation Report ---")

        summary = self.get_reconciliation_summary()
        logging.info("\nReconciliation Status Summary:")
        if "error" in summary:
            logging.error(f"  Error: {summary['error']}")
        elif not summary:
            logging.info("  No data available.")
        else:
            for status, count in summary.items():
                logging.info(f"  - {status.replace('_', ' ').title()}: {count}")

        anomalies = self.get_anomalous_events(limit=5)
        logging.info("\nTop 5 Anomalous Events:")
        if not anomalies:
            logging.info("  No anomalous events detected.")
        else:
            for anomaly in anomalies:
                logging.info(f"  - ID: {anomaly['id']}, Type: {anomaly['event_type']}, Source: {anomaly['source_system']}, Time: {anomaly['timestamp']}")
        
        logging.info("\n--- Report End ---")

    def close(self):
        if self.data_storage:
            self.data_storage.close_connection()

if __name__ == "__main__":
    reporter = FrenlyReporter()
    try:
        reporter.generate_report()
    except Exception as e:
        logging.critical(f"Failed to generate report: {e}")
    finally:
        reporter.close()
