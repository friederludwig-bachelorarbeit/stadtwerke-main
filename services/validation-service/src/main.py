import os
import json
import time
from contextlib import contextmanager
from config_logger import get_logger
from config_tracer import get_tracer
from utils import validate_message_with_schema, get_mqtt_topic_segment, on_assign
from MessageEvent import MessageEvent
from confluent_kafka import Consumer, Producer
from opentelemetry.propagate import inject, extract

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
KAFKA_CONSUMER_GROUP = "validation-group"
KAFKA_RAW_TOPIC = "raw-messages"
KAFKA_VALIDATED_TOPIC = "validated-messages"
KAFKA_ERROR_TOPIC = "error-messages"

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


def set_consumer_tracing_attributes(span, topic, message):
    """
    Setzt Tracing-Attribute für eine Kafka-Consumer-Nachricht.
    """
    span.set_attribute("kafka.consumer.topic", topic)
    span.set_attribute("kafka.message.offset", message.offset())
    span.set_attribute("kafka.message.partition", message.partition())


def set_producer_tracing_attributes(span, topic, message):
    """
    Setzt Tracing-Attribute für eine Kafka-Producer-Nachricht.
    """
    span.set_attribute("kafka.producer.topic", topic)
    span.set_attribute("kafka.producer.message_size", len(json.dumps(message)))


def process_message(payload, producer, headers):
    """
    Konsumiert Nachrichten aus Kafka, validiert sie und sendet 
    validierte oder fehlerhafte Nachrichten an die entsprechenden Kafka Topics.
    """
    # Trace-Kontext aus den Kafka-Headern extrahieren
    context = extract(headers)

    with tracer.start_as_current_span("process-message", context=context) as span:
        try:
            # JSON Schema validieren und Tracing-Attribute setzen
            is_valid, message = validate_message_with_schema(payload)
            span.set_attribute("kafka.message.valid", is_valid)
            span.set_attribute("kafka.message.payload_size", len(json.dumps(payload)))

            if is_valid:
                try:
                    # MQTT-Topic in Segmente aufteilen
                    mqtt_topics = payload["mqtt_topic"].split("/")

                    # Nachricht in MessageEvent umwandeln
                    msg = MessageEvent()
                    msg.standort = get_mqtt_topic_segment(mqtt_topics, 1)
                    msg.maschinentyp = get_mqtt_topic_segment(mqtt_topics, 2)
                    msg.maschinen_id = get_mqtt_topic_segment(mqtt_topics, 3)
                    msg.status_type = get_mqtt_topic_segment(mqtt_topics, 4)
                    msg.sensor_id = get_mqtt_topic_segment(mqtt_topics, 5)
                    msg.timestamp = payload.get("timestamp")
                    msg.value = payload.get("value", "")

                    msg_dict = msg.to_dict()

                    # Trace-Kontext einbetten
                    kafka_headers_dict = {}
                    inject(kafka_headers_dict)
                    kafka_headers = [(key, value.encode("utf-8"))
                                     for key, value in kafka_headers_dict.items()]

                    # Validierte Nachricht an Kafka senden
                    producer.produce(
                        KAFKA_VALIDATED_TOPIC,
                        value=json.dumps(msg_dict),
                        headers=kafka_headers)

                    # Tracing-Attribute setzen bei validierter Nachricht
                    set_producer_tracing_attributes(span, KAFKA_VALIDATED_TOPIC, msg_dict)

                    logger.info(f"Validierte Nachricht an {KAFKA_VALIDATED_TOPIC} gesendet: {msg_dict}")

                except IndexError as e:
                    error_payload = {
                        "original_message": payload,
                        "error": f"IndexError: {str(e)} - mqtt_topic enthält nicht genügend Segmente."
                    }
                    producer.produce(KAFKA_ERROR_TOPIC, value=json.dumps(error_payload))
                    set_producer_tracing_attributes(span, KAFKA_ERROR_TOPIC, error_payload)
                    span.record_exception(e)
                    logger.error(f"Fehlerhafte Nachricht an {KAFKA_ERROR_TOPIC} gesendet: {error_payload}")
            else:
                error_payload = {
                    "original_message": payload,
                    "error": message
                }
                producer.produce(KAFKA_ERROR_TOPIC, value=json.dumps(error_payload))
                set_producer_tracing_attributes(span, KAFKA_ERROR_TOPIC, error_payload)
                span.record_exception(Exception(message))
                logger.error(
                    f"Fehlerhafte Nachricht an {KAFKA_ERROR_TOPIC} gesendet: {error_payload}")

        except Exception as e:
            span.record_exception(e)
            logger.error(f"Fehler beim Verarbeiten der Nachricht: {e}")


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

                # Kafka-Header extrahieren und in ein Dictionary umwandeln
                headers_list = msg.headers() or []
                headers = {key: value.decode("utf-8") for key, value in headers_list}

                # Trace-Kontext aus Kafka-Headern extrahieren
                context = extract(headers)

                with tracer.start_as_current_span("consume-message", context=context) as span:
                    try:
                        payload = json.loads(msg.value().decode())

                        # Tracing-Attribute setzen
                        set_consumer_tracing_attributes(span, KAFKA_RAW_TOPIC, msg)

                        # Nachricht verarbeiten
                        process_message(payload, producer, headers)
                        consumer.store_offsets(msg)

                    except Exception as e:
                        span.record_exception(e)
                        logger.error(f"Fehler beim Verarbeiten der Nachricht: {e}")

        except KeyboardInterrupt:
            pass
        finally:
            logger.info("Validation Service beendet.")
