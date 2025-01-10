import os
import json
from validators.base import ProtocolMessageValidator
from message_event import MessageEvent


class MQTTMessageValidator(ProtocolMessageValidator):
    """
    Validator für MQTT-Nachrichten.
    """

    def __init__(self):
        # Pfad zur Schema-Datei
        schema_file_path = os.path.join(os.path.dirname(__file__), "mqtt_schema.json")

        # Schema aus der JSON-Datei laden
        with open(schema_file_path, "r") as schema_file:
            self.schema = json.load(schema_file)

    def validate(self, payload):
        """
        Validiert den MQTT-Payload und erstellt ein MessageEvent-Objekt.
        :param payload: Die MQTT-Message (Dictionary).
        :return: MessageEvent-Objekt, wenn die Nachricht gültig ist.
        :raises ValueError: Wenn die Nachricht ungültig ist.
        """
        # Basis-Schema-Validierung
        is_valid, error_message = self.validate_schema(payload, self.schema)
        if not is_valid:
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
            event_is_valid, errors = self.validate_message_event(msg)
            if not event_is_valid:
                error_msg = f"MessageEvent-Fehler: {', '.join(errors)}"
                raise ValueError(error_msg)

            return msg.to_dict()

        except IndexError as e:
            raise IndexError(f"IndexError: {e} - mqtt_topic enthält nicht genügend Segmente.")

        except KeyError as e:
            raise ValueError(f"Fehlendes erforderliches Feld im Payload: {e}")

        except Exception as e:
            raise ValueError(f"Fehler beim Verarbeiten der MQTT-Nachricht: {e}")
