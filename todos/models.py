import os

from django_extensions.db.models import ActivatorModel
from django.conf import settings
from django.db import models
from django.template.defaultfilters import truncatewords
from django.utils import timezone
from private_storage.fields import PrivateFileField


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


class Todo(Item):

    description = models.CharField(max_length=100)

    class Meta:
        ordering = ('activate_date',)

    def __str__(self):
        return self.description

    @property
    def string_value(self):
        return self.description


class Note(Item):

    text = models.TextField(blank=True)

    position = models.PositiveIntegerField()

    class Meta:
        ordering = ('position',)

    def __str__(self):
        return truncatewords(self.text, 7) if self.text else '...'

    @property
    def string_value(self):
        return self.text


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
