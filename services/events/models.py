from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class EventDate:
    date: date
    events: Optional[List[str]] = field(default_factory=lambda: [])
