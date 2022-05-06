from django.db import models
from django.utils.translation import gettext as _


class Widget(models.Model):

    WIDGET_TYPE_TODOS = 'todos'
    WIDGET_TYPE_FILES = 'files'
    WIDGET_TYPE_NOTES = 'notes'
    WIDGET_TYPE_EVENTS = 'events'
    WIDGET_TYPE_IMAGES = 'images'
    WIDGET_TYPE_SNIPPET = 'snippet'
    WIDGET_TYPE_UPLOAD = 'upload'

    WIDGET_TYPES = (
        (WIDGET_TYPE_TODOS, _("To do's")),
        (WIDGET_TYPE_FILES, _("Files")),
        (WIDGET_TYPE_NOTES, _("Notes")),
        (WIDGET_TYPE_EVENTS, _("Events")),
        (WIDGET_TYPE_IMAGES, _("Images")),
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
