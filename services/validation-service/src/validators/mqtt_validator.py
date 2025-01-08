from validators.base import ProtocolMessageValidator
from validators.message_event import MessageEvent
import logging

logger = logging.getLogger(__name__)


class MQTTMessageValidator(ProtocolMessageValidator):
    """
    Validator für MQTT-Nachrichten.

    Verwendet einen JSON-Schema-Validator, 
    um eingehende MQTT-Nachrichten zu validieren.
    """

    def __init__(self):
        self.schema = {
            "type": "object",
            "properties": {
                "timestamp": {
                    "type": "string",
                    "format": "date-time"
                },
                "value": {
                    "anyOf": [
                        {"type": "integer"},
                        {"type": "string"}
                    ]
                },
                "mqtt_topic": {"type": "string"},
                "protocol": {"type": "string"}
            },
            "required": ["timestamp", "mqtt_topic", "protocol"],
            "additionalProperties": True  # erlaube zusätzliche Felder
        }

    def validate(self, payload):
        """
        Validiert den MQTT-Payload und erstellt ein MessageEvent-Objekt.
        :param payload: Der MQTT-Payload (Dictionary).
        :return: MessageEvent-Objekt, wenn die Nachricht gültig ist.
        :raises ValueError: Wenn die Nachricht ungültig ist.
        """
        # Basis-Schema-Validierung
        is_valid, error_message = self.validate_json_with_schema(payload, self.schema)
        if not is_valid:
            logger.error(f"Schema-Validierung fehlgeschlagen: {error_message}")
            raise ValueError(f"Schema-Fehler: {error_message}")

        try:
            # MQTT-Topic in Segmente aufteilen
            mqtt_topics = payload["mqtt_topic"].split("/")

            # MessageEvent erstellen und Felder setzen
            msg = MessageEvent()
            msg.standort = mqtt_topics[1]
            msg.maschinentyp = mqtt_topics[2]
            msg.maschinen_id = mqtt_topics[3]
            msg.status_type = mqtt_topics[4]
            msg.sensor_id = mqtt_topics[5]
            msg.timestamp = payload.get("timestamp")
            msg.value = payload.get("value", "")

            # Validierung des MessageEvent-Objekts
            event_is_valid, errors = msg.is_valid()
            if not event_is_valid:
                error_msg = f"MessageEvent-Fehler: {', '.join(errors)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            return msg.to_dict()

        except IndexError as e:
            logger.error(f"IndexError: {e} - mqtt_topic enthält nicht genügend Segmente.")
            raise IndexError(f"IndexError: {e} - mqtt_topic enthält nicht genügend Segmente.")

        except KeyError as e:
            logger.error(f"Fehlendes erforderliches Feld im Payload: {e}")
            raise ValueError(f"Fehlendes erforderliches Feld im Payload: {e}")

        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten der MQTT-Nachricht: {e}")
            raise ValueError(f"Fehler beim Verarbeiten der MQTT-Nachricht: {e}")
