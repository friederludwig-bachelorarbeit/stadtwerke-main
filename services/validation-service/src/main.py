import os
import json
import time
from contextlib import contextmanager
from config.config_logger import get_logger
from config.config_tracer import get_tracer
from utils import on_assign, set_consumer_tracing_attributes, set_producer_tracing_attributes, handle_invalid_message, get_kafka_headers_dict, prepare_kafka_headers
from validator_factory import ValidatorFactory
from confluent_kafka import Consumer, Producer
from opentelemetry.propagate import inject, extract

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "validation-group")
KAFKA_RAW_TOPIC = os.getenv("KAFAK_RAW_TOPIC", "raw-messages")
KAFKA_VALIDATED_TOPIC = os.getenv("KAFKA_VALIDATED_TOPIC", "validated-messages")

logger = get_logger()
tracer = get_tracer()

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


def check_partitions(consumer, topic, retry_interval=5):
    """
    Überprüft, ob dem Consumer Partitionen zugewiesen sind.
    Wenn keine Partitionen zugewiesen sind, wird neu abonniert.
    """
    assigned_partitions = consumer.assignment()
    if not assigned_partitions:
        logger.warning("Keine Partitionen zugewiesen. Erneuter Versuch...")
        consumer.subscribe([topic], on_assign=on_assign)
        time.sleep(retry_interval)
        return False
    return True


def process_message(payload, producer, headers):
    """
    Konsumiert Nachrichten aus Kafka, validiert sie und sendet 
    validierte oder fehlerhafte Nachrichten an die entsprechenden Kafka Topics.
    """

    # Trace-Kontext aus Kafka-Header extrahieren
    context = extract(headers)

    with tracer.start_as_current_span("process-message", context=context) as span:
        span.set_attribute("kafka.message.payload_size", len(json.dumps(payload)))

        validator_factory = ValidatorFactory()

        # Protokoll ermitteln
        protocol = payload.get("protocol")
        if not protocol:
            handle_invalid_message(payload, producer, span, "Protokoll fehlt im Payload")
            return

        # Passenden Handler für das Protokoll abrufen
        validator = validator_factory.get_validator(protocol)
        if not validator:
            handle_invalid_message(payload, producer, span, f"Unbekanntes Protokoll: {protocol}")
            return

        # Validierung und Umwandlung der Nachricht
        try:
            msg_dict = validator(payload)
            span.set_attribute("kafka.message.valid", True)

            # Kafka-Header für Trace-Kontext vorbereiten
            kafka_headers_dict = {}
            inject(kafka_headers_dict)
            kafka_headers = prepare_kafka_headers(kafka_headers_dict)

            # Validierte Nachricht an Kafka senden
            producer.produce(
                KAFKA_VALIDATED_TOPIC,
                value=json.dumps(msg_dict),
                headers=kafka_headers
            )

            # Tracing-Attribute setzen bei validierter Nachricht
            set_producer_tracing_attributes(span, KAFKA_VALIDATED_TOPIC, msg_dict)
            span.set_attribute("kafka.message.valid", True)

            logger.info(f"Validierte Nachricht an {KAFKA_VALIDATED_TOPIC} gesendet: {msg_dict}")

        except Exception as e:
            handle_invalid_message(payload, producer, span, f"Fehler bei der Verarbeitung: {e}")


if __name__ == "__main__":
    logger.info("Validation Service gestartet.")
    with kafka_consumer() as consumer, kafka_producer() as producer:
        consumer.subscribe([KAFKA_RAW_TOPIC], on_assign=on_assign)

        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    if not check_partitions(consumer, KAFKA_RAW_TOPIC):
                        continue
                    continue
                if msg.error():
                    logger.error(f"Kafka-Fehler: {msg.error()}")
                    continue

                # Kafka-Header extrahieren und Trace-Kontext erstellen
                kafka_headers = get_kafka_headers_dict(msg.headers())
                context = extract(kafka_headers)

                with tracer.start_as_current_span("consume-message", context=context) as span:
                    try:
                        payload = json.loads(msg.value().decode())

                        # Tracing-Attribute setzen
                        set_consumer_tracing_attributes(span, KAFKA_RAW_TOPIC, msg)

                        # Nachricht verarbeiten
                        process_message(payload, producer, kafka_headers)
                        consumer.store_offsets(msg)

                    except Exception as e:
                        span.record_exception(e)
                        logger.error(f"Fehler beim Verarbeiten der Nachricht: {e}")

        except KeyboardInterrupt:
            pass
        finally:
            logger.info("Validation Service beendet.")
