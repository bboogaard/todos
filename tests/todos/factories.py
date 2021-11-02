import datetime
import hashlib

import factory
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from todos import models


class UserFactory(factory.django.DjangoModelFactory):

    username = 'tester'

    class Meta:
        model = User


class ItemFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Item
        abstract = True

    @factory.post_generation
    def item_id(obj, create, extracted, **kwargs):
        if not create:
            return

        obj.item_id = hashlib.md5(obj.string_value.encode()).hexdigest()


class TodoFactory(ItemFactory):

    description = 'Lorem'

    class Meta:
        model = models.Todo


class NoteFactory(ItemFactory):

    text = 'Lorem'

    position = factory.Sequence(lambda n: n)

    class Meta:
        model = models.Note


class EventFactory(factory.django.DjangoModelFactory):

    description = 'Lorem'

    date = factory.LazyAttribute(lambda obj: datetime.date.today())

    position = factory.Sequence(lambda n: n)

    class Meta:
        model = models.Event


class PrivateFileFactory(factory.django.DjangoModelFactory):

    file = ContentFile(b'Foo', name='foo.txt')

    class Meta:
        model = models.PrivateFile
