import os
import json
import time
from contextlib import contextmanager
from config import get_logger
from utils import validate_message_with_schema, get_mqtt_topic_segment, on_assign
from MessageEvent import MessageEvent
from confluent_kafka import Consumer, Producer

logger = get_logger()

# Kafka-Konfiguration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
KAFKA_CONSUMER_GROUP = "validation-group"

RAW_TOPIC = "raw-messages"
VALIDATED_TOPIC = "validated-messages"
ERROR_TOPIC = "error-messages"

consumer_settings = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': KAFKA_CONSUMER_GROUP,
    'auto.offset.reset': 'earliest',
    'enable.auto.offset.store': False
}


@contextmanager
def kafka_consumer():
    """
    Kontextmanager für den Kafka-Consumer.
    """
    consumer = Consumer(consumer_settings)
    try:
        yield consumer
    finally:
        consumer.close()


@contextmanager
def kafka_producer():
    """
    Kontextmanager für den Kafka-Producer.
    """
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
    try:
        yield producer
    finally:
        producer.flush()


def process_message(payload, producer):
    """
    Konsumiert Nachrichten aus Kafka, validiert sie und sendet 
    validierte oder fehlerhafte Nachrichten an die entsprechenden Topics.
    """
    is_valid, message = validate_message_with_schema(payload)

    if is_valid:
        try:
            mqtt_topics = payload["mqtt_topic"].split("/")

            # MessageEvent-Objekt erstellen
            msg = MessageEvent()
            msg.standort = get_mqtt_topic_segment(mqtt_topics, 1)
            msg.maschinentyp = get_mqtt_topic_segment(mqtt_topics, 2)
            msg.maschinen_id = get_mqtt_topic_segment(mqtt_topics, 3)
            msg.status_type = get_mqtt_topic_segment(mqtt_topics, 4)
            msg.sensor_id = get_mqtt_topic_segment(mqtt_topics, 5)
            msg.timestamp = payload.get("timestamp")
            msg.value = payload.get("value", "")

            msg_dict = msg.to_dict()
            producer.produce(VALIDATED_TOPIC, value=json.dumps(msg_dict))

            # Produziere validierte Nachricht
            logger.info(
                f"Validierte Nachricht an {VALIDATED_TOPIC} gesendet: {msg_dict}")

        except IndexError as e:
            error_payload = {
                "original_message": payload,
                "error": f"IndexError: {str(e)} - mqtt_topic enthält nicht genügend Segmente."
            }
            producer.produce(ERROR_TOPIC, value=json.dumps(error_payload))
            logger.error(
                f"Fehlerhafte Nachricht an {ERROR_TOPIC} gesendet: {error_payload}")
    else:
        error_payload = {
            "original_message": payload,
            "error": message
        }
        producer.produce(ERROR_TOPIC, value=json.dumps(error_payload))
        logger.error(
            f"Fehlerhafte Nachricht an {ERROR_TOPIC} gesendet: {error_payload}")


if __name__ == "__main__":
    logger.info("Validation Service gestartet.")

    with kafka_consumer() as consumer, kafka_producer() as producer:
        consumer.subscribe([RAW_TOPIC], on_assign=on_assign)

        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    # Überprüfe, ob Partitionen zugewiesen sind
                    assigned_partitions = consumer.assignment()
                    if not assigned_partitions:
                        logger.warning(
                            "Keine Partitionen zugewiesen. Erneuter Versuch...")
                        consumer.subscribe([RAW_TOPIC], on_assign=on_assign)
                        time.sleep(5)
                    continue
                if msg.error():
                    logger.error(f"Kafka-Fehler: {msg.error()}")
                    continue

                payload = json.loads(msg.value().decode())
                process_message(payload, producer)
                consumer.store_offsets(msg)

        except KeyboardInterrupt:
            pass
        finally:
            logger.info("Validation Service beendet.")
