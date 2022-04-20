import factory
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.utils.timezone import now

from api.data import models as data_models
from tests.todos.utils import generate_image
from todos import models


class UserFactory(factory.django.DjangoModelFactory):

    username = 'tester'

    class Meta:
        model = User


class TodoFactory(factory.django.DjangoModelFactory):

    description = 'Lorem'

    class Meta:
        model = data_models.Todo


class NoteFactory(factory.django.DjangoModelFactory):

    text = 'Lorem'

    class Meta:
        model = data_models.Note


class EventFactory(factory.django.DjangoModelFactory):

    description = 'Lorem'

    datetime = factory.LazyAttribute(lambda obj: now())

    class Meta:
        model = models.Event


class PrivateFileFactory(factory.django.DjangoModelFactory):

    file = ContentFile(b'Foo', name='foo.txt')

    class Meta:
        model = data_models.PrivateFile


class PrivateImageFactory(factory.django.DjangoModelFactory):

    image = ImageFile(generate_image(), name='foo.png')

    class Meta:
        model = models.PrivateImage


class HistoricalDateFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.HistoricalDate


class CodeSnippetFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = data_models.CodeSnippet
