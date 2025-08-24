import logging
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AnomalyDetector:
    def __init__(self, contamination=0.01, random_state=42):
        """
        Initializes the AnomalyDetector with an Isolation Forest model.
        contamination: The proportion of outliers in the data set.
        """
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self.is_trained = False
        logging.info(f"AnomalyDetector initialized with IsolationForest (contamination={contamination}).")

    def train(self, data_points: np.ndarray):
        """
        Trains the Isolation Forest model.
        data_points: A 2D numpy array where each row is a sample and columns are features.
        """
        if data_points.ndim == 1:
            data_points = data_points.reshape(-1, 1) # Reshape for single feature

        if data_points.size == 0:
            logging.warning("No data points provided for training the anomaly detector.")
            return

        logging.info(f"Training IsolationForest with {data_points.shape[0]} samples and {data_points.shape[1]} features.")
        self.model.fit(data_points)
        self.is_trained = True
        logging.info("IsolationForest model trained successfully.")

    def predict(self, data_point: Dict[str, Any], feature_key: str = 'value') -> Tuple[int, float]:
        """
        Predicts if a single data point is an anomaly and returns its anomaly score.
        data_point: The data dictionary containing the feature to check.
        feature_key: The key in the payload dictionary that holds the numerical feature for anomaly detection.
        Returns: (prediction, anomaly_score)
                 prediction: -1 for anomaly, 1 for normal.
                 anomaly_score: The lower, the more anomalous.
        """
        if not self.is_trained:
            logging.warning("AnomalyDetector model is not trained. Returning default normal prediction.")
            return 1, 0.0 # Default to normal if not trained

        payload = data_point.get('payload', {})
        feature_value = payload.get(feature_key)

        if feature_value is None or not isinstance(feature_value, (int, float)):
            logging.warning(f"Feature '{feature_key}' not found or not numerical in payload for ID {data_point.get('id', 'N/A')}. Cannot perform anomaly detection.")
            return 1, 0.0 # Cannot detect if feature is missing or not numerical

        # Reshape for single sample prediction
        sample = np.array([[feature_value]])

        prediction = self.model.predict(sample)[0]
        anomaly_score = self.model.decision_function(sample)[0]

        logging.info(f"Anomaly detection for ID {data_point.get('id', 'N/A')}: Prediction={prediction}, Score={anomaly_score}")
        return prediction, anomaly_score

if __name__ == "__main__":
    # Example Usage
    detector = AnomalyDetector(contamination=0.1)

    # Simulate historical data for training
    # Let's say we are monitoring 'transaction_amount' in the payload
    historical_data = [
        {"id": "t1", "payload": {"transaction_amount": 100}},
        {"id": "t2", "payload": {"transaction_amount": 120}},
        {"id": "t3", "payload": {"transaction_amount": 110}},
        {"id": "t4", "payload": {"transaction_amount": 150}},
        {"id": "t5", "payload": {"transaction_amount": 90}},
        {"id": "t6", "payload": {"transaction_amount": 1000}}, # Anomaly
        {"id": "t7", "payload": {"transaction_amount": 130}},
        {"id": "t8", "payload": {"transaction_amount": 80}},
        {"id": "t9", "payload": {"transaction_amount": 5000}}, # Anomaly
        {"id": "t10", "payload": {"transaction_amount": 105}},
    ]

    # Extract the feature for training
    training_features = np.array([d["payload"]["transaction_amount"] for d in historical_data if "transaction_amount" in d["payload"]])
    detector.train(training_features)

    print("\n--- Testing Anomaly Detection ---")

    # Test new incoming data
    new_data_normal = {"id": "new1", "payload": {"transaction_amount": 115}}
    pred, score = detector.predict(new_data_normal, feature_key="transaction_amount")
    print(f"Normal data (115): Prediction={pred}, Score={score}")

    new_data_anomaly = {"id": "new2", "payload": {"transaction_amount": 2000}}
    pred, score = detector.predict(new_data_anomaly, feature_key="transaction_amount")
    print(f"Anomaly data (2000): Prediction={pred}, Score={score}")

    new_data_missing_feature = {"id": "new3", "payload": {"other_key": 50}}
    pred, score = detector.predict(new_data_missing_feature, feature_key="transaction_amount")
    print(f"Missing feature data: Prediction={pred}, Score={score}")

    new_data_non_numerical_feature = {"id": "new4", "payload": {"transaction_amount": "abc"}}
    pred, score = detector.predict(new_data_non_numerical_feature, feature_key="transaction_amount")
    print(f"Non-numerical feature data: Prediction={pred}, Score={score}")
