from haystack import indexes

from todos.models import Event, Note, Todo


class SearchMixin:
    _model = None
    _updated_field = None

    def get_model(self):
        return self._model

    def get_updated_field(self):
        return self._updated_field


def search_index_factory(model, updated_field=None):
    return type(
        'SearchIndex{}'.format(model.__name__), (SearchMixin, indexes.SearchIndex, indexes.Indexable), {
            '_model': model,
            '_updated_field': updated_field or 'update_datetime',
            'text': indexes.CharField(document=True, use_template=True),
            'include_in_search': indexes.BooleanField(model_attr='include_in_search')
        }
    )


EventSearchIndex = search_index_factory(Event)
NoteSearchIndex = search_index_factory(Note)
TodoSearchIndex = search_index_factory(Todo)
