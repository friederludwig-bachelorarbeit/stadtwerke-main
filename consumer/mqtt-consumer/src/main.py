import os
import json
from contextlib import contextmanager
from config_logger import get_logger
from config_tracer import get_tracer
from utils import prepare_kafka_headers
from paho.mqtt.client import Client
from confluent_kafka import Producer
from opentelemetry.propagate import inject

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "stadtwerke/#")
KAFKA_PRODUCER_TOPIC = os.getenv("KAFKA_PRODUCER_TOPIC", "raw-messages")

logger = get_logger()
tracer = get_tracer()


@contextmanager
def kafka_producer():
    """ Kontextmanager für den Kafka-Producer."""
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
    try:
        yield producer
    finally:
        producer.flush()


def on_message(client, userdata, message, producer):
    """
    Callback-Funktion für eingehende MQTT-Nachrichten.
    Sendet die Nachricht an Kafka.
    """
    with tracer.start_as_current_span("process-mqtt-message") as span:
        try:
            topic = message.topic
            payload = json.loads(message.payload.decode())
            payload['mqtt_topic'] = topic
            payload['protocol'] = "mqtt"

            # Tracing-Attribute setzen
            span.set_attribute("mqtt.topic", topic)
            span.set_attribute("mqtt.payload_size", len(message.payload))
            span.set_attribute("mqtt.qos", message.qos)

            # Kafka-Header für Trace-Kontext vorbereiten
            kafka_headers_dict = {}
            inject(kafka_headers_dict)
            kafka_headers = prepare_kafka_headers(kafka_headers_dict)

            # Nachricht an Kafka senden
            with tracer.start_as_current_span("send-to-kafka") as kafka_span:
                producer.produce(
                    KAFKA_PRODUCER_TOPIC,
                    key=topic,
                    value=json.dumps(payload),
                    headers=kafka_headers
                )

                # Tracing-Attribute setzen
                kafka_span.set_attribute("kafka.topic", KAFKA_PRODUCER_TOPIC)
                kafka_span.set_attribute("kafka.message_size", len(json.dumps(payload)))

            logger.info(f"Nachricht an Kafka gesendet: {payload}")
        except json.JSONDecodeError:
            logger.error("Nachricht ist kein gültiges JSON.")
            span.record_exception(Exception("Invalid JSON"))
        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten der Nachricht: {e}")
            span.record_exception(e)


if __name__ == "__main__":
    mqtt_client = Client()

    # Fügt den Kafka-Producer der on_message Callback-Funktion hinzu
    with kafka_producer() as producer:
        def wrapped_on_message(client, userdata, message):
            on_message(client, userdata, message, producer)

        mqtt_client.on_message = wrapped_on_message

        try:
            # Mit MQTT-Broker verbinden und auf Nachrichten warten
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
            mqtt_client.subscribe(MQTT_TOPIC)
            logger.info(f"Verbunden mit MQTT-Broker {MQTT_BROKER}:{MQTT_PORT}")
            mqtt_client.loop_forever()
        except KeyboardInterrupt:
            mqtt_client.disconnect()
        except Exception as e:
            logger.error(f"Fehler bei der Verbindung mit MQTT-Broker: {e}")
            mqtt_client.disconnect()
