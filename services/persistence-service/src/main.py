import os
import json
import time
from contextlib import contextmanager
from config_logger import get_logger
from config_tracer import get_tracer
from utils import on_assign
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from confluent_kafka import Consumer
from opentelemetry.propagate import extract

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
KAFKA_CONSUMER_TOPIC = "validated-messages"
KAFKA_CONSUMER_GROUP = "persistence-group"
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

logger = get_logger()
tracer = get_tracer()

consumer_settings = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': KAFKA_CONSUMER_GROUP,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
}


@contextmanager
def kafka_consumer():
    """ Kontextmanager für den Kafka-Consumer."""
    consumer = Consumer(consumer_settings)
    consumer.subscribe([KAFKA_CONSUMER_TOPIC])
    try:
        yield consumer
    finally:
        consumer.close()


@contextmanager
def influxdb_client_manager():
    """ Kontextmanager für den InfluxDB-Client."""
    client = InfluxDBClient(
        url=INFLUXDB_URL,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG
    )
    try:
        yield client.write_api(write_options=SYNCHRONOUS)
    finally:
        client.close()


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


def set_kafka_tracing_attributes(span, topic, message):
    """
    Setzt Tracing-Attribute für Kafka-Nachrichten.
    """
    span.set_attribute("kafka.consumer.topic", topic)
    span.set_attribute("kafka.message.offset", message.offset())
    span.set_attribute("kafka.message.partition", message.partition())
    span.set_attribute("message.payload_size", len(message.value()))


def set_influxdb_tracing_attributes(span, bucket, tags):
    """
    Setzt Tracing-Attribute für InfluxDB.
    """
    span.set_attribute("db.operation", "write")
    span.set_attribute("db.system", "influxdb")
    span.set_attribute("influxdb.bucket", bucket)
    for tag_key, tag_value in tags.items():
        span.set_attribute(f"data.tag.{tag_key}", tag_value)


def store_in_influxdb(payload, write_api, context):
    """ Speichert die Daten aus Kafka in InfluxDB. """
    with tracer.start_as_current_span("store-in-influxdb", context=context) as span:
        try:
            # InfluxDB-Daten aus der Payload
            timestamp = payload.get("timestamp")
            measurement = payload.get("measurement")  # Der Messungstyp, z. B. status_type
            tags = payload.get("tags", {})
            fields = payload.get("fields", {})

            # Tracing-Attribute setzen
            set_influxdb_tracing_attributes(span, INFLUXDB_BUCKET, tags)

            # Datenpunkt erstellen
            point = Point(measurement).time(timestamp)

            # Tags hinzufügen
            for tag_key, tag_value in tags.items():
                point = point.tag(tag_key, tag_value)

            # Fields hinzufügen
            for field_key, field_value in fields.items():
                point = point.field(field_key, field_value)

            # Datenpunkt in die Datenbank schreiben
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)
            logger.info(f"Nachricht gespeichert: {payload}")

        except Exception as e:
            span.record_exception(e)
            logger.error(f"Fehler beim Speichern in InfluxDB: {e}")


if __name__ == "__main__":
    logger.info("Persistence Service gestartet.")

    with kafka_consumer() as consumer, influxdb_client_manager() as write_api:
        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    if not check_partitions(consumer, KAFKA_CONSUMER_TOPIC):
                        continue
                    continue

                if msg.error():
                    logger.error(f"Kafka-Fehler: {msg.error()}")
                    continue

                # Kafka-Header extrahieren und Trace-Kontext erstellen
                headers = msg.headers() or []
                headers_dict = {key: value.decode("utf-8") for key, value in headers}
                context = extract(headers_dict)

                with tracer.start_as_current_span("consume-message", context=context) as span:
                    try:
                        # Nachricht verarbeiten und speichern
                        payload = json.loads(msg.value().decode())
                        set_kafka_tracing_attributes(span, KAFKA_CONSUMER_TOPIC, msg)
                        store_in_influxdb(payload, write_api, context)
                        consumer.commit(asynchronous=False)

                    except Exception as e:
                        span.record_exception(e)
                        logger.error(f"Fehler beim Verarbeiten der Nachricht: {e}")
        except KeyboardInterrupt:
            pass
        finally:
            logger.info("Persistence Service beendet.")
