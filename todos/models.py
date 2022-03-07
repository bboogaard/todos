import datetime
import os

import pytz
from django_extensions.db.models import ActivatorModel
from django.conf import settings
from django.db import models
from django.template.defaultfilters import truncatewords
from django.utils import timezone
from django.utils.translation import gettext as _
from taggit.managers import TaggableManager
from private_storage.fields import PrivateFileField, PrivateImageField

from lib.datetime import date_range


class SearchMixin(models.Model):

    update_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def search_type(self):
        raise NotImplementedError()

    @property
    def result_params(self):
        return {}

    @property
    def include_in_search(self):
        return True

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
    def result_params(self):
        params = super().result_params
        if self.is_inactive:
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
    def result_params(self):
        params = super().result_params
        params.update(({
            'note_id': self.item_id
        }))
        return params

    @property
    def include_in_search(self):
        return self.is_active

    @property
    def search_field(self):
        return self.text

    @property
    def search_result(self):
        return self.text


class EventMixin:

    @property
    def event_date(self):
        raise NotImplementedError()

    @property
    def event_key(self):
        raise NotImplementedError()


class Event(EventMixin, SearchMixin, models.Model):

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
    def event_date(self):
        dt = self.datetime_localized.date()
        return dt.day, dt.month

    @property
    def event_key(self):
        return self.datetime

    @property
    def search_type(self):
        return 'Event'

    @property
    def result_params(self):
        params = super().result_params
        params.update({
            'year': self.datetime.year,
            'month': self.datetime.month
        })
        return params

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


class BasePrivateFile(SearchMixin, models.Model):

    created = models.DateTimeField(auto_now_add=True)

    tags = TaggableManager()

    class Meta:
        abstract = True
        ordering = ('-created',)

    @property
    def search_field(self):
        return ' '.join(map(str, self.tags.all()))

    def save_file(self, file):
        file_field = self.get_file_field()
        file_field.save(file.name, file)

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
            'image_id': self.pk
        })
        return params

    @property
    def search_result(self):
        return self.image.name

    def get_file_field(self):
        return self.image


class Widget(models.Model):

    WIDGET_TYPE_TODOS = 'todos'
    WIDGET_TYPE_FILES = 'files'
    WIDGET_TYPE_NOTES = 'notes'
    WIDGET_TYPE_EVENTS = 'events'
    WIDGET_TYPE_IMAGES = 'images'
    WIDGET_TYPE_DATES = 'dates'
    WIDGET_TYPE_SNIPPET = 'snippet'
    WIDGET_TYPE_UPLOAD = 'upload'

    WIDGET_TYPES = (
        (WIDGET_TYPE_TODOS, _("To do's")),
        (WIDGET_TYPE_FILES, _("Files")),
        (WIDGET_TYPE_NOTES, _("Notes")),
        (WIDGET_TYPE_EVENTS, _("Events")),
        (WIDGET_TYPE_IMAGES, _("Images")),
        (WIDGET_TYPE_DATES, _("Historical dates")),
        (WIDGET_TYPE_SNIPPET, _("Code snippets")),
        (WIDGET_TYPE_UPLOAD, _("Upload")),
    )

    type = models.CharField(max_length=8, choices=WIDGET_TYPES, unique=True)

    title = models.CharField(max_length=32)

    is_enabled = models.BooleanField(default=False)

    position = models.PositiveIntegerField()

    refresh_interval = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('position',)

    def __str__(self):
        return self.title

    @property
    def widget_id(self):
        return '{}-{}'.format(self.pk, self.type)

    @property
    def refresh_interval_msecs(self):
        return 1000 * self.refresh_interval if self.refresh_interval else None


class HistoricalDateManager(models.Manager):

    def for_date_range(self, start: datetime.date, end: datetime.date):
        date_filter = models.Q()
        for date in date_range(start, end):
            date_filter |= models.Q(date__month=date.month, date__day=date.day)
        return self.filter(date_filter)


class HistoricalDate(EventMixin, models.Model):

    date = models.DateField()

    event = models.CharField(max_length=255)

    objects = HistoricalDateManager()

    class Meta:
        ordering = ('date__month', 'date__day', 'date__year')

    def __str__(self):
        return self.event

    @property
    def event_date(self):
        return self.date.day, self.date.month

    @property
    def event_key(self):
        return self.date


class CodeSnippet(models.Model):

    text = models.TextField(blank=True)

    position = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ('position',)

    def __str__(self):
        return truncatewords(self.text, 7) if self.text else '...'

    def save(self, *args, **kwargs):
        if self._state.adding:
            manager = self.__class__.objects
            self.position = (manager.aggregate(max_pos=models.Max('position'))['max_pos'] or 0) + 1
        super().save(*args, **kwargs)
