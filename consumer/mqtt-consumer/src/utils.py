def prepare_kafka_headers(headers_dict):
    """
    Wandelt ein Dictionary mit Headern in eine Liste von Kafka-kompatiblen Header-Tuples um.
    :param headers_dict: Dictionary mit Headern (Key-Value-Paare).
    :return: Liste von Kafka-Headern (Tuples), wobei die Werte UTF-8-kodiert sind.
    """
    return [(key, value.encode("utf-8")) for key, value in headers_dict.items()]
