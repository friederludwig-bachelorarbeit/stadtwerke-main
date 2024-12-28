import os
import json
from src.config import get_logger
from src.utils import validate_message_with_schema
from confluent_kafka import Consumer, Producer

logger = get_logger()

# Kafka-Konfiguration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "locahost:9092")
RAW_TOPIC = "raw-messages"
VALIDATED_TOPIC = "validated-messages"
ERROR_TOPIC = "error-messages"


# Kafka-Consumer und Producer konfigurieren
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'validation-service',
    'auto.offset.reset': 'earliest'
})

producer = Producer({'bootstrap.servers': KAFKA_BROKER})


def process_messages():
    """
    Konsumiert Nachrichten aus Kafka, validiert sie und sendet validierte oder fehlerhafte Nachrichten
    an die entsprechenden Topics.
    """
    consumer.subscribe([RAW_TOPIC])

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            # logger.error(f"Kafka-Fehler: {msg.error()}")
            continue

        try:
            payload = json.loads(msg.value().decode('utf-8'))
            is_valid, message = validate_message_with_schema(payload)

            if is_valid:
                producer.produce(VALIDATED_TOPIC, json.dumps(
                    payload).encode('utf-8'))
                logger.info(
                    f"Validierte Nachricht an {VALIDATED_TOPIC} gesendet: {payload}")
                producer.flush()
            else:
                error_payload = {
                    "original_message": payload,
                    "error": message
                }
                producer.produce(ERROR_TOPIC, json.dumps(
                    error_payload).encode('utf-8'))
                logger.error(
                    f"Fehlerhafte Nachricht an {ERROR_TOPIC} gesendet: {error_payload}")
                producer.flush()
        except json.JSONDecodeError:
            logger.error(
                "Ungültiges JSON-Format in der empfangenen Nachricht.")
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {e}")


if __name__ == "__main__":
    logger.info("Validation Service gestartet.")
    try:
        process_messages()
    except KeyboardInterrupt:
        consumer.close()
    finally:
        logger.info("Validation Service beendet.")
        consumer.close()
