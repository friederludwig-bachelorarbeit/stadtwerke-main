
class MessageEvent:
    def __init__(self):
        self.timestamp = None
        self._standort = None
        self._maschinentyp = None
        self._maschinen_id = None
        self._status_type = None
        self._value = None
        self._sensor_id = None

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

    @property
    def standort(self):
        return self._standort

    @standort.setter
    def standort(self, value):
        self._standort = value

    @property
    def maschinentyp(self):
        return self._maschinentyp

    @maschinentyp.setter
    def maschinentyp(self, value):
        self._maschinentyp = value

    @property
    def maschinen_id(self):
        return self._maschinen_id

    @maschinen_id.setter
    def maschinen_id(self, value):
        self._maschinen_id = value

    @property
    def status_type(self):
        return self._status_type

    @status_type.setter
    def status_type(self, value):
        self._status_type = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def sensor_id(self):
        return self._sensor_id

    @sensor_id.setter
    def sensor_id(self, value):
        self._sensor_id = value

    def to_dict(self):
        return {
            "standort": self._standort,
            "maschinentyp": self._maschinentyp,
            "maschinen_id": self._maschinen_id,
            "status_type": self._status_type,
            "value": self._value,
            "sensor_id": self._sensor_id,
        }