import pika
import json
import logging
import time # Added for batch processing timeout
from .data_validator_cleanser import DataValidatorCleanser
from .frenly_data_storage import FrenlyDataStorage
from .conflict_resolver import ConflictResolver
from .anomaly_detector import AnomalyDetector
import numpy as np # Needed for anomaly detector training example
from multiprocessing import Pool # For distributed computing simulation
from .distributed_processor import simulate_heavy_computation # For distributed computing simulation
from .frenly_alerter import FrenlyAlerter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FrenlyDataStreamConsumer:
    def __init__(self, rabbitmq_host='localhost', queue_name='frenly_data_stream'):
        self.rabbitmq_host = rabbitmq_host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.validator_cleanser = DataValidatorCleanser()
        self.data_storage = FrenlyDataStorage()
        self.data_storage.connect() # Establish DB connection on consumer init
        self.conflict_resolver = ConflictResolver()
        self.anomaly_detector = AnomalyDetector()

        # TODO: In a real application, the anomaly detector should be trained on historical data.
        # For demonstration, we'll use a dummy training set.
        # This should ideally be loaded from a persistent store or a dedicated training pipeline.
        dummy_training_data = np.array([
            100, 120, 110, 150, 90, 130, 80, 105, 112, 98, 103, 125, 95, 108, 118
        ]).reshape(-1, 1) # Reshape for single feature
        self.anomaly_detector.train(dummy_training_data)
        self.alerter = FrenlyAlerter()
        self.message_buffer = []
        self.batch_size = 10 # Process 10 messages at a time
        self.batch_timeout = 5 # seconds
        self.last_batch_time = time.time() # Initialize last batch time

    def connect(self):
        try:
            logging.info(f"Attempting to connect to RabbitMQ at {self.rabbitmq_host}...")
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            logging.info(f"Connected to RabbitMQ and declared queue: {self.queue_name}")
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def on_message_callback(self, ch, method, properties, body):
        try:
            self.message_buffer.append((ch, method, properties, body))
            if len(self.message_buffer) >= self.batch_size or (time.time() - self.last_batch_time) >= self.batch_timeout:
                self._process_batch()
        except Exception as e:
            logging.error(f"Error buffering message: {e}", exc_info=True)
            # If buffering itself fails, we might need to nack the message here
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def _process_batch(self):
        if not self.message_buffer:
            return

        logging.info(f"Processing batch of {len(self.message_buffer)} messages.")
        messages_to_ack = []
        messages_to_nack = []

        processed_messages_for_pool = []
        original_messages_map = {} # Map original message (ch, method, etc.) to its processed data

        for ch, method, properties, body in self.message_buffer:
            try:
                data = json.loads(body.decode('utf-8'))
                logging.info(f"Received raw message: {data}")

                # Validate the incoming data
                is_valid, validation_msg = self.validator_cleanser.validate(data)
                if not is_valid:
                    logging.error(f"Validation failed for message (ID: {data.get('id', 'N/A')}): {validation_msg}. Message will not be processed.")
                    messages_to_nack.append((method.delivery_tag, False)) # Nack and don't requeue invalid messages
                    continue

                # Cleanse the data
                cleansed_data = self.validator_cleanser.cleansed(data)
                logging.info(f"Received and cleansed message (ID: {cleansed_data.get('id', 'N/A')}): {cleansed_data})")

                # Fetch existing data for conflict resolution
                existing_data = self.data_storage.get_data_by_id(cleansed_data['id'])

                # Resolve conflicts
                final_data = self.conflict_resolver.resolve(incoming_data=cleansed_data, existing_data=existing_data)
                
                # Prepare data for distributed processing
                processed_messages_for_pool.append(final_data)
                original_messages_map[final_data['id']] = (ch, method, properties, body) # Store original message for ack/nack

            except json.JSONDecodeError:
                logging.error(f"Failed to decode JSON from message: {body.decode('utf-8')}")
                messages_to_nack.append((method.delivery_tag, False)) # Nack and don't requeue malformed messages
            except Exception as e:
                logging.error(f"Error preparing message for batch processing: {e}", exc_info=True)
                messages_to_nack.append((method.delivery_tag, True)) # Nack and requeue on other processing error

        if processed_messages_for_pool:
            logging.info(f"Sending {len(processed_messages_for_pool)} messages for simulated distributed computation.")
            # Use multiprocessing Pool for parallel processing
            # The number of processes should ideally be based on CPU cores
            with Pool(processes=4) as pool: # Using 4 processes for demonstration
                processed_results = pool.map(simulate_heavy_computation, processed_messages_for_pool)

            for final_data_processed in processed_results:
                original_ch, original_method, _, _ = original_messages_map[final_data_processed['id']]
                try:
                    # Store the resolved and processed data
                    self.data_storage.insert_data(final_data_processed)

                    # Perform anomaly detection
                    prediction, anomaly_score = self.anomaly_detector.predict(final_data_processed, feature_key='transaction_amount')
                    if prediction == -1:
                        alert_msg = f"Anomaly detected for ID {final_data_processed.get('id', 'N/A')}: Score={anomaly_score}. Feature: {final_data_processed.get('payload', {}).get('transaction_amount', 'N/A')}."
                        self.alerter.send_alert(alert_msg, "warning", final_data_processed.get('id', 'N/A'))
                        # TODO: Update reconciliation_status in DB to 'anomaly'
                    else:
                        logging.info(f"Data for ID {final_data_processed.get('id', 'N/A')} is normal. Score={anomaly_score}.")

                    messages_to_ack.append(original_method.delivery_tag)

                except psycopg2.Error as e:
                    error_msg = f"Critical: Database error during data insertion for ID {final_data_processed.get('id', 'N/A')}: {e}"
                    self.alerter.send_alert(error_msg, "critical", final_data_processed.get('id', 'N/A'))
                    logging.error(error_msg)
                    messages_to_nack.append((original_method.delivery_tag, True)) # Nack and requeue on DB error
                except Exception as e:
                    logging.error(f"Error processing message after distributed computation: {e}", exc_info=True)
                    messages_to_nack.append((original_method.delivery_tag, True)) # Nack and requeue on other processing error

        # Acknowledge/Nack all messages in the batch
        for tag in messages_to_ack:
            self.channel.basic_ack(delivery_tag=tag)
            logging.info(f"Message acknowledged: {tag}")
        for tag, requeue in messages_to_nack:
            self.channel.basic_nack(delivery_tag=tag, requeue=requeue)
            logging.info(f"Message nacked: {tag}, requeue={requeue}")

        self.message_buffer = [] # Clear buffer after processing
        self.last_batch_time = time.time()

    def start_consuming(self):
        if not self.channel:
            logging.error("RabbitMQ channel not established. Call connect() first.")
            return

        logging.info(f"Starting to consume messages from queue: {self.queue_name}")
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.on_message_callback)
        
        # Use a non-blocking consumer to allow for batch timeout
        # This requires pika to be configured for non-blocking operation,
        # or using a separate thread for batch processing.
        # For simplicity, we'll use a blocking consumer with a timeout check
        # in the callback, which is not ideal for true non-blocking.
        # A better approach would be to use pika's AsyncoreConnection or SelectConnection.
        # For this example, we'll simulate the timeout check within the blocking loop.
        
        # To enable batching with timeout in a blocking consumer,
        # you'd typically use basic_get and a loop with time.sleep,
        # or pika's asynchronous adapters.
        
        # Given the current structure, the timeout will only trigger
        # when a new message arrives after the timeout period.
        # To make it truly time-based, we'd need to change the consumer model.
        # For now, the batching is primarily size-based, with a soft timeout.
        
        try:
            # This will block and call on_message_callback for each message
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logging.info("Consumer stopped by user.")
        except Exception as e:
            logging.error(f"Error during consumption: {e}", exc_info=True)
        finally:
            # Process any remaining messages in the buffer before closing
            self._process_batch()
            self.close_connection()

    def close_connection(self):
        if self.connection and self.connection.is_open:
            logging.info("Closing RabbitMQ connection.")
            self.connection.close()
        self.data_storage.close_connection() # Close DB connection

if __name__ == "__main__":
    consumer = FrenlyDataStreamConsumer()
    try:
        consumer.connect()
        consumer.start_consuming()
    except Exception as e:
        logging.critical(f"Consumer failed to start: {e}")
    finally:
        consumer.close_connection()