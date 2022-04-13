from django_extensions.db.models import ActivatorModel, ActivatorModelManager as BaseActivatorModelManager
from django.db import models
from django.utils.timezone import now

from todos.models import SearchMixin


class ActivatorModelManager(BaseActivatorModelManager):

    def deactivate(self, ids):
        self.get_queryset().filter(pk__in=ids).update(
            status=ActivatorModel.INACTIVE_STATUS,
            deactivate_date=now()
        )


class Todo(SearchMixin, ActivatorModel):

    description = models.CharField(max_length=100)

    objects = ActivatorModelManager()

    def __str__(self):
        return self.description

    @property
    def string_value(self):
        return self.description

    @property
    def search_type(self):
        return 'Todo'

    @property
    def result_params(self):
        params = super().result_params
        if self.status == self.INACTIVE_STATUS:
            params.update({
                'description': self.description
            })
        return params

    @property
    def search_field(self):
        return self.description

    @property
    def search_result(self):
        return self.description
