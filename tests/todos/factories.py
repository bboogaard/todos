import hashlib

import factory

from todos import models


class TodoFactory(factory.django.DjangoModelFactory):

    description = 'Lorem'

    class Meta:
        model = models.Todo

    @factory.post_generation
    def item_id(self, create, extracted, **kwargs):
        if not create:
            return

        self.item_id = hashlib.md5(self.description.encode()).hexdigest()
