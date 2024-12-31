import os
import json
import time
from contextlib import contextmanager
from config import get_logger
from utils import on_assign
from confluent_kafka import Consumer
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

logger = get_logger()

# Kafka-Konfiguration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
KAFKA_CONSUMER_TOPIC = "validated-messages"
KAFKA_CONSUMER_GROUP = "persistence-group"

# InfluxDB-Konfiguration
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "stadtwerke")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "iot_data")

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


def store_in_influxdb(payload, write_api):
    """ Speichert die Daten aus Kafka in InfluxDB. """
    try:
        timestamp = payload.get("timestamp")
        standort = payload.get("standort")
        maschinen_id = payload.get("maschinen_id")
        maschinentyp = payload.get("maschinentyp")
        status_type = payload.get("status_type")
        sensor_id = payload.get("sensor_id")
        value = payload.get("value")

        # Datenpunkt erstellen
        point = (
            Point(status_type)
            .tag("standort", standort)
            .tag("maschinentyp", maschinentyp)
            .tag("maschinen_id", maschinen_id)
            .field("value", value)
            .time(timestamp)
        )

        # Sensor-ID als Tag hinzufügen, falls vorhanden
        if sensor_id:
            point = point.tag("sensor_id", sensor_id)

        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        logger.info(f"Nachricht gespeichert: {payload}")
    except Exception as e:
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
                try:
                    payload = json.loads(msg.value().decode())
                    store_in_influxdb(payload, write_api)
                    consumer.commit(asynchronous=False)
                except Exception as e:
                    logger.error(f"Fehler beim Speichern der Nachricht: {e}")

        except KeyboardInterrupt:
            pass
        finally:
            logger.info("Persistence Service beendet.")
