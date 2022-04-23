from datetime import datetime
from typing import Dict, Tuple

import pytz
from dataclasses import dataclass
from django.conf import settings
from django.utils.timezone import make_aware

from api.views.internal.utils import dataclass_from_dict


class ViewModel:

    @classmethod
    def from_dict(cls, d: Dict):
        return dataclass_from_dict(cls, d, cls.get_coerce_map())

    @staticmethod
    def get_coerce_map():
        return None


@dataclass
class Image(ViewModel):
    id: int
    name: str
    url: str
    thumbnail: str
    image: str


@dataclass
class Event(ViewModel):
    id: int
    description: str
    datetime: datetime
    event_date: Tuple[int, int]

    def __str__(self):
        return self.description

    @property
    def datetime_localized(self):
        return self.datetime.astimezone(pytz.timezone(settings.TIME_ZONE))

    @staticmethod
    def get_coerce_map():

        def _from_iso(dt: str) -> datetime:
            date_part = dt[:19]
            return make_aware(datetime.strptime(date_part, '%Y-%m-%dT%H:%M:%S'))

        return {
            'datetime': _from_iso,
            'event_date': tuple
        }
