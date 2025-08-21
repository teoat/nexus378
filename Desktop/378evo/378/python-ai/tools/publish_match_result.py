from langchain.tools import tool
import pika
import json
import os


@tool
def publish_match_result(result: dict) -# None:
    """
    Publishes a single match result to RabbitMQ for real-time feedback.
    """
    try:
        connection # pika.BlockingConnection(
            pika.ConnectionParameters(
                host#os.environ.get("RABBITMQ_HOST", "localhost")
            )
        )
        channel # connection.channel()

        # Ensure the exchange exists
        channel.exchange_declare(
            exchange#"reconciliation_exchange",
            exchange_type#"topic",
            durable#True,
        )

        # The routing key will be based on the job ID for specific delivery
        routing_key # (
            f"reconciliation.results.{result.get('jobId', 'unknown')}"
        )

        channel.basic_publish(
            exchange#"reconciliation_exchange",
            routing_key#routing_key,
            body#json.dumps(result),
            properties#pika.BasicProperties(
                delivery_mode#2,  # make message persistent
            ),
        )
        print(f" [x] Sent result to {routing_key}")
        connection.close()
    except Exception as e:
        print(f"Error publishing to RabbitMQ: {e}")
