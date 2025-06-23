import json
from datetime import datetime


class JSONSerializer:
    """
    A JSON serializer with support for custom type encoding and decoding.

    This class extends the standard JSON serialization to handle additional
    Python types, particularly datetime objects. It provides methods to encode
    Python objects to JSON strings and decode JSON strings back to Python objects.
    """

    def __init__(self):
        # Define custom encoders for specific types
        self.encoders = {datetime: lambda obj: {"__datetime__": obj.isoformat()}}

        # Define custom decoders for specific type markers
        self.decoders = {"__datetime__": lambda obj: datetime.fromisoformat(obj)}

    def encode(self, obj) -> str:
        return json.dumps(obj, default=self._encode_object)

    def decode(self, json_str: str):
        try:
            return json.loads(json_str, object_hook=self._decode_object)
        except json.decoder.JSONDecodeError:
            return {}

    def _encode_object(self, obj) -> dict:
        for type_, encoder in self.encoders.items():
            if isinstance(obj, type_):
                return encoder(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def _decode_object(self, obj: dict):
        if not isinstance(obj, dict):
            return obj

        special_type = next((key for key in self.decoders.keys() if key in obj), None)
        if special_type:
            return self.decoders[special_type](obj[special_type])
        return obj
