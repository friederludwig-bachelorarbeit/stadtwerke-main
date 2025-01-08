import os
import json
from config.config_logger import get_logger

KAFKA_ERROR_TOPIC = os.getenv("KAFAK_ERROR_TOPIC", "error-messages")

logger = get_logger()


def on_assign(consumer, partitions):
    logger.info(f"Partitions assigned: {partitions}")
    consumer.assign(partitions)


def set_consumer_tracing_attributes(span, topic, message):
    """
    Setzt Tracing-Attribute für eine Kafka-Consumer-Nachricht.
    """
    span.set_attribute("kafka.consumer.topic", topic)
    span.set_attribute("kafka.message.offset", message.offset())
    span.set_attribute("kafka.message.partition", message.partition())


def set_producer_tracing_attributes(span, topic, message, attributes=None):
    """
    Setzt Tracing-Attribute für eine Kafka-Producer-Nachricht.
    """
    span.set_attribute("kafka.producer.topic", topic)
    span.set_attribute("kafka.producer.message_size", len(json.dumps(message)))

    if attributes and isinstance(attributes, dict):
        for key, value in attributes.items():
            span.set_attribute(f"{key}", value)
    elif attributes is not None:
        raise ValueError("The 'attributes' parameter must be a dictionary or None.")


def handle_invalid_message(payload, producer, span, error_message):
    """
    Behandelt ungültige Nachrichten und sendet sie an das Fehler-Topic.
    """
    error_payload = {
        "original_message": payload,
        "error": error_message
    }
    producer.produce(KAFKA_ERROR_TOPIC, value=json.dumps(error_payload))
    set_producer_tracing_attributes(span, KAFKA_ERROR_TOPIC, error_payload, {
        "kafka.message.valid": False,
        "service.error": f"{error_message}"})
    span.record_exception(Exception(error_message))
    logger.error(f"Fehlerhafte Nachricht an {KAFKA_ERROR_TOPIC} gesendet: {error_payload}")
