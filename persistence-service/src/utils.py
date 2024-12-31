from config import get_logger

logger = get_logger()

# Kafka-Event-Handler
def on_assign(consumer, partitions):
    logger.info(f"Partitions assigned: {partitions}")
    consumer.assign(partitions)

def on_revoke(consumer, partitions):
    try:
        # Prüfe, ob es Partitionen gibt, die einen gültigen Offset haben (-1001 = kein Offset)
        partitions_to_commit = [p for p in partitions if p.offset != -1001]
        if partitions_to_commit:
            consumer.commit(asynchronous=False)
            logger.info(f"Partitions revoked: {partitions}")
    except Exception as e:
        logger.error(f"Fehler beim Commit vor Revoke: {e}")
