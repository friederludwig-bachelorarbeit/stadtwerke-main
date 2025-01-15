import os
from loguru import logger

# Zentraler Pfad zur Logdatei
BASE_DIR = "../"  # Projekt-Root
LOG_FILE_PATH = os.path.join(BASE_DIR, "var", "logs", "service.log")

LOG_NAME = "persistence-service"

# Logger konfigurieren
logger.add(
    LOG_FILE_PATH,
    format="{time} [{level}] [{extra[service]}] {message}"
)


def get_logger():
    """
    Gibt einen Logger zurück, der mit dem Servicenamen gebunden ist.
    :return: Logger-Instanz
    """
    return logger.bind(log_name=LOG_NAME, service=LOG_NAME)
