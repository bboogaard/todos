from typing import List

from django.template.loader import render_to_string

from .models import EventDate


class EventMessageFactory:

    @classmethod
    def create(cls, events: List[EventDate]) -> str:
        return render_to_string('messages/upcoming_events.txt', {'events': events})
