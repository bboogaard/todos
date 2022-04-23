from typing import Any, Callable, Dict, Optional

from dacite import from_dict
from dataclasses import dataclass


def dataclass_from_dict(cls: dataclass, d: Dict, coerce_map: Optional[Dict[str, Callable[[Any], Any]]] = None):
    if coerce_map:
        for key, coerce in coerce_map.items():
            d[key] = coerce(d[key])
    return from_dict(cls, d)
