from django_extensions.db.models import ActivatorModel, ActivatorModelManager as BaseActivatorModelManager
from django.conf import settings
from django.db import models
from django.template.defaultfilters import truncatewords
from django.utils.timezone import now
from private_storage.fields import PrivateFileField, PrivateImageField
from private_storage.storage import private_storage

from todos.models import SearchMixin


class ActivatorModelManager(BaseActivatorModelManager):

    def activate(self, ids):
        self.get_queryset().filter(pk__in=ids).update(
            status=ActivatorModel.ACTIVE_STATUS,
            activate_date=now()
        )

    def deactivate(self, ids):
        self.get_queryset().filter(pk__in=ids).update(
            status=ActivatorModel.INACTIVE_STATUS,
            deactivate_date=now()
        )


class PrivateFileManager(models.Manager):

    def delete_with_file(self, ids):
        queryset = self.get_queryset().filter(pk__in=ids)
        filenames = [obj.filename for obj in queryset]
        result = queryset.delete()
        for filename in filenames:
            private_storage.delete(filename)
        return result


class PositionedModel(models.Model):

    position = models.PositiveIntegerField(unique=True)

    class Meta:
        abstract = True
        ordering = ('-position',)

    def save(self, *args, **kwargs):
        if self._state.adding and not self.position:
            manager = self.__class__.objects
            self.position = (manager.aggregate(max_pos=models.Max('position'))['max_pos'] or 0) + 1
        super().save(*args, **kwargs)


class Todo(SearchMixin, ActivatorModel):

    description = models.CharField(max_length=100)

    objects = ActivatorModelManager()

    class Meta:
        ordering = ('-activate_date',)

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


class Note(SearchMixin, PositionedModel, ActivatorModel):

    text = models.TextField(blank=True)

    objects = ActivatorModelManager()

    class Meta:
        ordering = ('-position',)

    def __str__(self):
        return truncatewords(self.text, 7) if self.text else '...'

    @property
    def string_value(self):
        return self.text

    @property
    def search_type(self):
        return 'Note'

    @property
    def result_params(self):
        params = super().result_params
        params.update(({
            'note_id': self.pk
        }))
        return params

    @property
    def include_in_search(self):
        return self.status == self.ACTIVE_STATUS

    @property
    def search_field(self):
        return self.text

    @property
    def search_result(self):
        return self.text


class CodeSnippet(PositionedModel):

    text = models.TextField(blank=True)

    def __str__(self):
        return truncatewords(self.text, 7) if self.text else '...'


class BasePrivateFile(SearchMixin, models.Model):

    created = models.DateTimeField(auto_now_add=True)

    objects = PrivateFileManager()

    class Meta:
        abstract = True
        ordering = ('-created',)

    @property
    def search_field(self):
        return self.filename

    @property
    def filename(self):
        file_field = self.get_file_field()
        return file_field.name

    def save_file(self, file, filename: str = ''):
        file_field = self.get_file_field()
        file_field.save(filename or file.name, file)

    def get_file_field(self):
        raise NotImplementedError()

    def search_type(self):
        raise NotImplementedError()

    def search_result(self):
        raise NotImplementedError()


class PrivateFile(BasePrivateFile):

    file = PrivateFileField()

    def __str__(self):
        return self.file.name

    def get_absolute_url(self):
        return settings.MEDIA_URL + self.file.name

    @property
    def search_type(self):
        return 'File'

    @property
    def result_params(self):
        params = super().result_params
        params.update({
            'file_id': self.pk
        })
        return params

    @property
    def search_result(self):
        return self.file.name

    def get_file_field(self):
        return self.file


class PrivateImage(BasePrivateFile):

    image = PrivateImageField()

    def __str__(self):
        return self.image.name

    def get_absolute_url(self):
        return settings.MEDIA_URL + self.image.name

    @property
    def search_type(self):
        return 'Image'

    @property
    def result_params(self):
        params = super().result_params
        params.update({
            'id': self.pk
        })
        return params

    @property
    def search_result(self):
        return self.image.name

    def get_file_field(self):
        return self.image
