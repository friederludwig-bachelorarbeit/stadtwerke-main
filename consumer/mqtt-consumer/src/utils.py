import json


def prepare_kafka_headers(headers_dict):
    """
    Wandelt ein Dictionary mit Headern in eine Liste von Kafka-kompatiblen Header-Tuples um.
    :param headers_dict: Dictionary mit Headern (Key-Value-Paare).
    :return: Liste von Kafka-Headern (Tuples), wobei die Werte UTF-8-kodiert sind.
    """
    return [(key, value.encode("utf-8")) for key, value in headers_dict.items()]


def set_mqtt_tracing_attributes(span, topic, message):
    """
    Setzt Tracing-Attribute für Kafka-Nachrichten.
    """
    span.set_attribute("mqtt.topic", topic)
    span.set_attribute("mqtt.payload_size", len(message.payload))
    span.set_attribute("mqtt.qos", message.qos)


def set_kafka_tracing_attributes(span, topic, payload):
    """
    Setzt Tracing-Attribute für Kafka-Nachrichten.
    """
    span.set_attribute("kafka.topic", topic)
    span.set_attribute("kafka.message_size", len(json.dumps(payload)))
