from haystack import indexes

from api.data.models import Note, PrivateFile, PrivateImage, Todo
from todos.models import Event


class SearchMixin:
    _model = None
    _updated_field = None

    def get_model(self):
        return self._model

    def get_updated_field(self):
        return self._updated_field


def search_index_factory(model, updated_field=None, auto_complete_field=None):
    attrs = {
        '_model': model,
        '_updated_field': updated_field or 'update_datetime',
        'text': indexes.CharField(document=True, use_template=True),
        'include_in_search': indexes.BooleanField(model_attr='include_in_search'),
        'text_auto': indexes.EdgeNgramField(model_attr=model.get_autocomplete_field())
    }
    return type(
        'SearchIndex{}'.format(model.__name__), (SearchMixin, indexes.SearchIndex, indexes.Indexable), attrs
    )


EventSearchIndex = search_index_factory(Event)
NoteSearchIndex = search_index_factory(Note)
TodoSearchIndex = search_index_factory(Todo)
FileSearchIndex = search_index_factory(PrivateFile)
ImageSearchIndex = search_index_factory(PrivateImage)
