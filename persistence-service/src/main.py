import os
import json
import time
from config import get_logger
from utils import on_assign
from confluent_kafka import Consumer
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

logger = get_logger()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
KAFKA_CONSUMER_TOPIC = "validated-messages"
KAFKA_CONSUMER_GROUP = "persistence-group"

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "stadtwerke")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_ORG", "iot_data")

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': KAFKA_CONSUMER_GROUP,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
})
consumer.subscribe([KAFKA_CONSUMER_TOPIC])

influxdb_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
influxdb_write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)


def store_in_influxdb(payload):
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

        influxdb_write_api.write(bucket=INFLUXDB_BUCKET, record=point)

        # Commit nach erfolgreicher Verarbeitung
        try:
            consumer.commit(asynchronous=False)
        except Exception as e:
            logger.error(f"Fehler beim Commit: {e}")

        logger.info(f"Nachricht gespeichert: {payload}")
    except Exception as e:
        logger.error(f"Fehler beim Speichern in InfluxDB: {e}")


if __name__ == "__main__":
    logger.info("Persistence Service gestartet.")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # Überprüfe, ob Partitionen zugewiesen sind
                assigned_partitions = consumer.assignment()
                if not assigned_partitions:
                    logger.warning(
                        "Keine Partitionen zugewiesen. Erneuter Versuch...")
                    consumer.subscribe(
                        [KAFKA_CONSUMER_TOPIC], on_assign=on_assign)
                    time.sleep(5)
                continue
            if msg.error():
                logger.error(f"Kafka-Fehler: {msg.error()}")
                continue

            payload = json.loads(msg.value().decode())

            try:
                store_in_influxdb(payload)

            except Exception as e:
                logger.error(f"Fehler beim Speichern der Nachricht: {e}")

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Persistence Service beendet.")
        consumer.close()
        influxdb_client.close()
