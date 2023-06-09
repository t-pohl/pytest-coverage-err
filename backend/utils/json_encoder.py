import json
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class CustomEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> str:
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj.hex)
        if isinstance(obj, datetime):
            return str(obj)
        if isinstance(obj, Enum):
            return str(obj.value)
        return str(json.JSONEncoder.default(self, obj))
