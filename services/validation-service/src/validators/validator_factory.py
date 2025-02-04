from validators.mqtt_validator import MQTTMessageValidator
from validators.coap_validator import CoAPMessageValidator


class ValidatorFactory:
    @staticmethod
    def get_validator(protocol_type):
        if protocol_type == "mqtt":
            return MQTTMessageValidator()
        elif protocol_type == "coap":
            return CoAPMessageValidator()
        else:
            return None
