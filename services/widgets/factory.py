from typing import Optional

from services.widgets.service import CodeSnippetWidgetRenderer, DatesWidgetRenderer, EventsWidgetRenderer, \
    FilesWidgetRenderer, ImagesWidgetRenderer, NotesWidgetRenderer, TodosWidgetRenderer, UploadWidgetRenderer, \
    WidgetRendererService
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
        elif widget.type == Widget.WIDGET_TYPE_IMAGES:
            return ImagesWidgetRenderer(widget)
        elif widget.type == Widget.WIDGET_TYPE_DATES:
            return DatesWidgetRenderer(widget)
        elif widget.type == Widget.WIDGET_TYPE_SNIPPET:
            return CodeSnippetWidgetRenderer(widget)
        elif widget.type == Widget.WIDGET_TYPE_UPLOAD:
            return UploadWidgetRenderer(widget)
        else:
            raise NotImplementedError()
