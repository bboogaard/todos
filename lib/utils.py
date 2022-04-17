import re
from typing import Any, Callable, Dict

camelize_re = re.compile(r"[a-z0-9]?_[a-z0-9]")


def underscore_to_camel(match):
    group = match.group()
    if len(group) == 3:
        return group[0] + group[2].upper()
    else:
        return group[1].upper()


def camelize(value: str) -> str:
    return re.sub(camelize_re, underscore_to_camel, value)


def with_camel_keys(data: Dict, recursive: bool = False) -> Dict:
    return _convert_dict(data, camelize, recursive=recursive)


def _convert_dict(data: Dict, convert_func: Callable, recursive: bool = False) -> Dict:
    keys_map = {
        key: convert_func(key)
        for key in data.keys()
        if isinstance(key, str)
    }
    return {
        keys_map.get(key, key): _get_dict_val(lambda v: _convert_dict(v, convert_func, True), val) if recursive else val
        for key, val in data.items()
    }


def _get_dict_val(caller: Callable, val: Any):
    if isinstance(val, dict):
        return caller(val)
    elif isinstance(val, list):
        return [caller(d) for d in val if all([isinstance(d, dict) for d in val])]
    else:
        return val
