from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from todos.models import Event


@dataclass
class EventDate:
    date: date
    events: Optional[List[Event]] = field(default_factory=lambda: [])
