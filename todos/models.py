from django_extensions.db.models import ActivatorModel
from django.db import models
from django.utils import timezone


class Todo(ActivatorModel):

    description = models.CharField(max_length=100)

    todo_id = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.description

    @property
    def is_active(self):
        return self.status == self.ACTIVE_STATUS

    @property
    def is_inactive(self):
        return self.status == self.INACTIVE_STATUS

    def activate(self):
        self.activate_date = None
        self.status = self.ACTIVE_STATUS
        self.save()

    def soft_delete(self):
        if self.status == self.INACTIVE_STATUS:
            return

        self.status = self.INACTIVE_STATUS
        self.deactivate_date = timezone.now()

        self.save()
