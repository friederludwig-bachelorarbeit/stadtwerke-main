import time
from config_logger import get_logger

logger = get_logger()


def on_assign(consumer, partitions):
    logger.info(f"Partitions assigned: {partitions}")
    consumer.assign(partitions)


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


def get_headers_dict(headers):
    """
    Wandelt Kafka-Header in ein Dictionary um.
    :param headers: Liste der Kafka-Header (Tuple von Key und Value).
    :return: Dictionary mit dekodierten Headern.
    """
    return {key: value.decode("utf-8") for key, value in (headers or [])}
