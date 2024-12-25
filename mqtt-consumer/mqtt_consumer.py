import json
from paho.mqtt.client import Client
from confluent_kafka import Producer

MQTT_BROKER = "mqtt-broker"
MQTT_PORT = 1883
MQTT_TOPIC = "stadtwerke/#"
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "raw-messages"

# Kafka-Producer konfigurieren
producer = Producer({'bootstrap.servers': KAFKA_BROKER})


def on_message(client, userdata, message):
    """
      Callback Funktion für eingehende MQTT-Nachrichten.
    """
    try:
        topic = message.topic
        payload = json.loads(message.payload.decode())
        producer.produce(KAFKA_TOPIC, key=message.topic,
                         value=json.dumps(payload))
        producer.flush()
        print(f"Nachricht an Kafka gesendet: {payload}")
    except json.JSONDecodeError:
        print("❌ Nachricht ist kein gültiges JSON.")
    except Exception as e:
        print(f"❌ Ein Fehler ist aufgetreten: {e}")


# MQTT-Client konfigurieren
mqtt_client = Client()
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.subscribe(MQTT_TOPIC)
mqtt_client.loop_forever()
