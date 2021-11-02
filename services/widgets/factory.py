from typing import Optional

from services.widgets.service import EventsWidgetRenderer, FilesWidgetRenderer, NotesWidgetRenderer, \
    TodosWidgetRenderer, WidgetRendererService
from todos.models import Widget


class WidgetRendererFactory:

    @classmethod
    def get_renderer(cls, widget: Widget) -> Optional[WidgetRendererService]:
        if widget.type == Widget.WIDGET_TYPE_FILES:
            return FilesWidgetRenderer(widget)
        elif widget.type == Widget.WIDGET_TYPE_NOTES:
            return NotesWidgetRenderer(widget)
        elif widget.type == Widget.WIDGET_TYPE_TODOS:
            return TodosWidgetRenderer(widget)
        elif widget.type == Widget.WIDGET_TYPE_EVENTS:
            return EventsWidgetRenderer(widget)
        else:
            raise NotImplementedError()