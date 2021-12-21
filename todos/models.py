import os

import pytz
from django_extensions.db.models import ActivatorModel
from django.conf import settings
from django.db import models
from django.template.defaultfilters import truncatewords
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.translation import gettext as _
from private_storage.fields import PrivateFileField


class SearchMixin:

    @property
    def search_type(self):
        raise NotImplementedError()

    @property
    def result_url(self):
        raise NotImplementedError()

    @property
    def search_field(self):
        raise NotImplementedError()

    @property
    def search_result(self):
        raise NotImplementedError()


class Item(ActivatorModel):

    item_id = models.CharField(max_length=32, unique=True)

    class Meta(ActivatorModel.Meta):
        abstract = True

    @property
    def string_value(self):
        raise NotImplementedError()

    @property
    def is_active(self):
        return self.status == self.ACTIVE_STATUS

    @property
    def is_inactive(self):
        return self.status == self.INACTIVE_STATUS

    def activate(self):
        if self.status == self.ACTIVE_STATUS:
            return

        self.activate_date = None
        self.status = self.ACTIVE_STATUS
        self.save()

    def soft_delete(self):
        if self.status == self.INACTIVE_STATUS:
            return

        self.status = self.INACTIVE_STATUS
        self.deactivate_date = timezone.now()

        self.save()


class Todo(SearchMixin, Item):

    description = models.CharField(max_length=100)

    def __str__(self):
        return self.description

    @property
    def string_value(self):
        return self.description

    @property
    def search_type(self):
        return 'Todo'

    @property
    def result_url(self):
        return reverse('todos:index') + '?' + urlencode({
            'q': self.description
        })

    @property
    def search_field(self):
        return self.description

    @property
    def search_result(self):
        return self.description


class Note(SearchMixin, Item):

    text = models.TextField(blank=True)

    position = models.PositiveIntegerField()

    def __str__(self):
        return truncatewords(self.text, 7) if self.text else '...'

    @property
    def string_value(self):
        return self.text

    @property
    def search_type(self):
        return 'Note'

    @property
    def result_url(self):
        return reverse('todos:index')

    @property
    def search_field(self):
        return self.text

    @property
    def search_result(self):
        return self.text


class Event(SearchMixin, models.Model):

    description = models.CharField(max_length=100)

    datetime = models.DateTimeField()

    message_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ('datetime',)

    def __str__(self):
        return self.description

    @property
    def datetime_localized(self):
        return self.datetime.astimezone(pytz.timezone(settings.TIME_ZONE))

    @property
    def search_type(self):
        return 'Event'

    @property
    def result_url(self):
        return reverse('todos:index') + '?' + urlencode({
            'year': self.datetime.year,
            'month': self.datetime.month
        })

    @property
    def search_field(self):
        return self.description

    @property
    def search_result(self):
        return self.description


class GalleryQuerySet(models.QuerySet):

    def with_images(self):
        queryset = self._clone()
        queryset = queryset.filter(
            models.Exists(
                Wallpaper.objects.filter(
                    gallery=models.OuterRef('pk')
                )
            )
        )

        return queryset


class Gallery(models.Model):

    name = models.CharField(max_length=32, unique=True)

    objects = GalleryQuerySet.as_manager()

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Wallpaper(models.Model):

    image = models.ImageField(upload_to='wallpapers/')

    gallery = models.ForeignKey(Gallery, related_name='wallpapers', on_delete=models.CASCADE)

    position = models.PositiveIntegerField()

    class Meta:
        ordering = ('position',)

    def __str__(self):
        return self.image.file.name

    def get_image_url(self):
        return settings.MEDIA_URL + 'wallpapers/' + os.path.basename(self.image.file.name)


class PrivateFile(models.Model):

    created = models.DateTimeField(auto_now_add=True)

    file = PrivateFileField()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.file.name

    def get_absolute_url(self):
        return settings.MEDIA_URL + self.file.name


class Widget(models.Model):

    WIDGET_TYPE_TODOS = 'todos'
    WIDGET_TYPE_FILES = 'files'
    WIDGET_TYPE_NOTES = 'notes'
    WIDGET_TYPE_EVENTS = 'events'

    WIDGET_TYPES = (
        (WIDGET_TYPE_TODOS, _("To do's")),
        (WIDGET_TYPE_FILES, _("Files")),
        (WIDGET_TYPE_NOTES, _("Notes")),
        (WIDGET_TYPE_EVENTS, _("Events")),
    )

    type = models.CharField(max_length=8, choices=WIDGET_TYPES, unique=True)

    title = models.CharField(max_length=32)

    is_enabled = models.BooleanField(default=False)

    position = models.PositiveIntegerField()

    class Meta:
        ordering = ('position',)

    def __str__(self):
        return self.title
