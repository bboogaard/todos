# Dynamic settings provider
import inspect
from typing import Any, Dict, List, Optional, Tuple

from django.core.cache import cache
from django.core.validators import EMPTY_VALUES


class SettingsField:

    def __init__(self, default: Any = None):
        self.default = default

    def serialize(self, value: Any) -> str:
        if value in EMPTY_VALUES:
            return ''

        return str(value)

    def deserialize(self, value: str) -> Any:
        return self.to_python(value)

    def to_python(self, value: Any) -> Any:
        return value

    def get_value(self, value: Any) -> Any:
        value = self.to_python(value)
        if value in EMPTY_VALUES:
            value = self.default

        return value

    def as_str(self, value: Any) -> str:
        return str(self.get_value(value))


class CharField(SettingsField):

    def to_python(self, value: Any) -> str:
        if value in EMPTY_VALUES:
            return ''

        return str(value)


class IntegerField(SettingsField):

    def to_python(self, value: Any) -> Optional[int]:
        if value in EMPTY_VALUES:
            return None

        return int(value)


class BoundField:

    def __init__(self, value: Any, field: SettingsField):
        self.value = value
        self.field = field

    def __str__(self):
        return self.field.as_str(self.value)

    def __eq__(self, other):
        return self.field.get_value(self.value) == self.field.to_python(other)


class BoundSettings:

    def __init__(self, values: Dict[str, BoundField]):
        self.values = values

    def __getitem__(self, item) -> BoundField:
        return self.values[item]


class BaseCacheSettings:

    def __init__(self, name: str):
        self.name = name

        self.cache = cache
        self._settings = None
        self._fields = None

    def load(self, **defaults):
        if self._settings is None:
            self._settings = self._load_settings(**defaults)

        return BoundSettings({
            key: BoundField(val, self._get_field(key))
            for key, val in self._settings.items()
        })

    def save(self, **values):
        for name, value in values.items():
            self._get_field(name)
            self._settings.update({
                name: value
            })
        raw_settings = {
            key: field.serialize(self._settings.get(key))
            for key, field in self.fields
        }
        self.cache.set(self.name, raw_settings, timeout=None)

    @property
    def fields(self) -> List[Tuple[str, SettingsField]]:
        if self._fields is None:
            self._fields = self._get_fields()

        return self._fields

    def _load_settings(self, **defaults) -> Dict:
        raw_settings = self.cache.get(self.name, {}) or {}
        if not isinstance(raw_settings, dict):
            raise TypeError("Expected dict for {}, got {}".format(self.name, type(raw_settings)))

        def _load_value(_key: str, _field: SettingsField) -> Any:
            value = _field.deserialize(raw_settings.get(_key, ''))
            if value in EMPTY_VALUES and _key in defaults:
                value = defaults.get(_key)
            return value

        return {
            key: _load_value(key, field)
            for key, field in self.fields
        }

    def _get_fields(self) -> List[Tuple[str, SettingsField]]:
        return inspect.getmembers(self.__class__, lambda attr: isinstance(attr, SettingsField))

    def _get_field(self, name) -> SettingsField:
        field = next(filter(lambda f: f[0] == name, self.fields), None)
        if field is None:
            raise ValueError("Field not found: {}".format(name))

        return field[1]
