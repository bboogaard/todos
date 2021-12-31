import datetime
import os
import shutil
import uuid
from io import BytesIO
from zipfile import ZipFile

import pytz
from django_webtest import WebTest
from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.management import call_command
from PIL import Image
from pyquery import PyQuery
from webtest import Upload

from todos.models import Event, Note, PrivateFile, PrivateImage, Todo, Wallpaper, Widget
from todos.settings import cache_settings
from tests.todos.factories import EventFactory, NoteFactory, PrivateFileFactory, PrivateImageFactory, TodoFactory, \
    UserFactory
from tests.todos.utils import generate_image


class TodosViewTest(WebTest):

    with_fixtures = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if cls.with_fixtures:
            call_command('loaddata', 'wallpapers.json')
            call_command('loaddata', 'widgets.json')
            call_command('collectmedia', '--noinput')

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_user = UserFactory()


class TestIndexView(TodosViewTest):

    def test_get(self):
        response = self.app.get('/', user=self.test_user)
        self.assertEqual(response.status_code, 200)


class TestSearchView(TodosViewTest):

    def setUp(self):
        super().setUp()
        self.todos = [
            TodoFactory(description='Foo'),
            TodoFactory(description='Bar', status=Note.INACTIVE_STATUS)
        ]
        self.notes = [
            NoteFactory(text='Foo'),
            NoteFactory(text='Bar', status=Note.INACTIVE_STATUS),
        ]
        self.events = [
            EventFactory(description='Foo')
        ]
        call_command('rebuild_index', interactive=False)

    def test_get(self):
        response = self.app.get('/search/?q=Foo', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        response.mustcontain('Foo - Todo', 'Foo - Note', 'Foo - Event')

    def test_get_inactive(self):
        response = self.app.get('/search/?q=Bar', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        response.mustcontain('Bar - Todo', no=['Bar - Note'])


class TestTodosSaveJson(TodosViewTest):

    csrf_checks = False

    def test_post(self):
        data = {
            'items': ['Pay bills', 'Take out trash', 'Call mom']
        }
        response = self.app.post('/todos-save.json', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)

        result = list(Todo.objects.order_by('description').values_list('description', flat=True))
        expected = ['Call mom', 'Pay bills', 'Take out trash']
        self.assertEqual(result, expected)


class TestTodosActivateJson(TodosViewTest):

    csrf_checks = False

    def test_post(self):
        TodoFactory(description='Done', status=Todo.INACTIVE_STATUS)
        data = {
            'items': ['Done']
        }
        response = self.app.post('/todos-activate.json', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)

        todo = Todo.objects.get(description='Done')
        self.assertTrue(todo.is_active)


class TestNotesSaveJson(TodosViewTest):

    csrf_checks = False

    def test_post(self):
        data = {
            'items': ['Pay bills', 'Take out trash', 'Call mom'],
            'index': '1'
        }
        response = self.app.post('/notes-save.json', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)

        result = list(Note.objects.order_by('text').values_list('text', flat=True))
        expected = ['Call mom', 'Pay bills', 'Take out trash']
        self.assertEqual(result, expected)

        result = cache.get('notes-index', 0)
        expected = 1
        self.assertEqual(result, expected)

    def test_post_invalid_index(self):
        data = {
            'items': ['Pay bills', 'Take out trash', 'Call mom'],
            'index': 'foo'
        }
        response = self.app.post('/notes-save.json', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)

        result = list(Note.objects.order_by('text').values_list('text', flat=True))
        expected = ['Call mom', 'Pay bills', 'Take out trash']
        self.assertEqual(result, expected)

        result = cache.get('notes-index', 0)
        expected = 0
        self.assertEqual(result, expected)


class TestSettingsSave(TodosViewTest):

    csrf_checks = False

    def test_post(self):
        data = {
            'todos_provider': 'remote'
        }
        response = self.app.post('/settings-save', data, user=self.test_user)
        self.assertEqual(response.status_code, 302)

        settings = cache_settings.load()
        self.assertEqual(settings.todos_provider, 'remote')


class TestWallpaperListView(TodosViewTest):

    with_fixtures = True

    def test_get(self):
        response = self.app.get('/wallpapers/list', user=self.test_user)
        self.assertEqual(response.status_code, 200)


class TestWallpaperCreateView(TodosViewTest):

    with_fixtures = True

    csrf_checks = False

    def test_get(self):
        response = self.app.get('/wallpapers/create', user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        img = Image.new(mode="RGB", size=(1, 1))
        fh = BytesIO()
        img.save(fh, format='PNG')

        data = {
            'gallery': '3',
            'image': Upload('wallpaper.png', fh.getvalue()),
            'position': '0'
        }

        response = self.app.post('/wallpapers/create', data, user=self.test_user)
        self.assertEqual(response.status_code, 302, response.content)
        self.assertEqual(Wallpaper.objects.count(), 4)

    def test_post_with_error(self):
        img = Image.new(mode="RGB", size=(1, 1))
        fh = BytesIO()
        img.save(fh, format='PNG')

        data = {
            'gallery': '3',
            'image': Upload('wallpaper.png', fh.getvalue())
        }

        response = self.app.post('/wallpapers/create', data, user=self.test_user)
        self.assertEqual(response.status_code, 200, response.content)


class TestWallpaperEditView(TodosViewTest):

    with_fixtures = True

    csrf_checks = False

    def test_get(self):
        response = self.app.get('/wallpapers/8/update', user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        img = Image.new(mode="RGB", size=(1, 1))
        fh = BytesIO()
        img.save(fh, format='PNG')

        data = {
            'gallery': '3',
            'image': Upload('wallpaper.png', fh.getvalue()),
            'position': '0'
        }

        response = self.app.post('/wallpapers/8/update', data, user=self.test_user)
        self.assertEqual(response.status_code, 302, response.content)

    def test_post_with_error(self):
        img = Image.new(mode="RGB", size=(1, 1))
        fh = BytesIO()
        img.save(fh, format='PNG')

        data = {
            'gallery': '3',
            'image': Upload('wallpaper.png', fh.getvalue())
        }

        response = self.app.post('/wallpapers/8/update', data, user=self.test_user)
        self.assertEqual(response.status_code, 200, response.content)


class TestWallpaperDeleteView(TodosViewTest):

    with_fixtures = True

    csrf_checks = False

    def test_post(self):
        data = {
            'wallpaper': [8]
        }
        response = self.app.post('/wallpapers/delete', data, user=self.test_user)
        self.assertEqual(response.status_code, 302, response.content)
        self.assertEqual(Wallpaper.objects.count(), 2)


class FileViewTest(TodosViewTest):

    file_type = None

    upload_file = None

    model = None

    file_field = None

    def _get(self, path, status_code=200):
        response = self.app.get('/files/{}/{}'.format(self.file_type, path), user=self.test_user)
        self.assertEqual(response.status_code, status_code)

    def _post(self, path, data, status_code=302, count=1):
        response = self.app.post('/files/{}/{}'.format(self.file_type, path), data, user=self.test_user)
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(self.model.objects.count(), count)
        if count:
            pfile = self.model.objects.first()
            self.assertEqual(getattr(pfile, self.file_field).read(), self.upload_file)
            self.assertEqual('.'.join(map(str, pfile.tags.all())), 'Foo')


class FileTestMixin:

    file_type = 'file'

    upload_file = b'Foo'

    model = PrivateFile

    file_field = 'file'


class TestFileListView(FileTestMixin, FileViewTest):

    def test_get(self):
        self._get('list')


class TestFileCreateView(FileTestMixin, FileViewTest):

    csrf_checks = False

    def test_get(self):
        self._get('create')

    def test_post(self):
        data = {
            'file': Upload('file.txt', self.upload_file, 'text/plain'),
            'tags': 'Foo'
        }

        self._post('create', data)

    def test_post_with_error(self):
        data = {
            'file': '',
            'tags': 'Foo'
        }

        self._post('create', data, status_code=200, count=0)


class TestFileUpdateView(FileTestMixin, FileViewTest):

    csrf_checks = False

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.file = PrivateFileFactory()
        cls.file.tags.add('Foo')

    def test_get(self):
        self._get('{}/update'.format(self.file.pk))

    def test_post(self):
        data = {
            'file': Upload('file.txt', self.upload_file, 'text/plain'),
            'tags': 'Foo'
        }

        self._post('{}/update'.format(self.file.pk), data)

    def test_post_with_error(self):
        data = {
            'file': '',
            'tags': ''
        }

        self._post('{}/update'.format(self.file.pk), data, status_code=200)


class TestFileDeleteView(FileTestMixin, FileViewTest):

    csrf_checks = False

    def test_post(self):
        pfile = PrivateFileFactory()
        data = {
            'file': [pfile.pk]
        }

        self._post('delete', data, count=0)


class ImageTestMixin:

    file_type = 'image'

    upload_file = generate_image().getvalue()

    model = PrivateImage

    file_field = 'image'


class TestImageListView(ImageTestMixin, FileViewTest):

    def test_get(self):
        self._get('list')


class TestImageCreateView(ImageTestMixin, FileViewTest):

    csrf_checks = False

    def test_get(self):
        self._get('create')

    def test_post(self):
        data = {
            'image': Upload('foo.png', self.upload_file, 'image/png'),
            'tags': 'Foo'
        }

        self._post('create', data)

    def test_post_with_error(self):
        data = {
            'image': '',
            'tags': 'Foo'
        }

        self._post('create', data, status_code=200, count=0)


class TestImageUpdateView(ImageTestMixin, FileViewTest):

    csrf_checks = False

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.file = PrivateImageFactory()
        cls.file.tags.add('Foo')

    def test_get(self):
        self._get('{}/update'.format(self.file.pk))

    def test_post(self):
        data = {
            'image': Upload('foo.png', self.upload_file, 'image/png'),
            'tags': 'Foo'
        }

        self._post('{}/update'.format(self.file.pk), data)

    def test_post_with_error(self):
        data = {
            'image': '',
            'tags': ''
        }

        self._post('{}/update'.format(self.file.pk), data, status_code=200)


class TestImageDeleteView(ImageTestMixin, FileViewTest):

    csrf_checks = False

    def test_post(self):
        pfile = PrivateImageFactory()
        data = {
            'file': [pfile.pk]
        }

        self._post('delete', data, count=0)


class TestTodosImportView(TodosViewTest):

    csrf_checks = False

    def test_get(self):
        response = self.app.get('/todos-import', user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = {
            'file': Upload('file.txt', b'Lorem\nIpsum', 'text/plain')
        }

        response = self.app.post('/todos-import', data, user=self.test_user)
        self.assertEqual(response.status_code, 302, response.content)
        result = list(Todo.objects.order_by('description').values_list('description', flat=True))
        expected = ['Ipsum', 'Lorem']
        self.assertEqual(result, expected)

    def test_post_with_error(self):
        data = {
            'file': ''
        }

        response = self.app.post('/todos-import', data, user=self.test_user)
        self.assertEqual(response.status_code, 200, response.content)


class TestTodosExportView(TodosViewTest):

    def test_get(self):
        TodoFactory(description='Lorem')
        TodoFactory(description='Ipsum')
        response = self.app.get('/todos-export', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'Lorem\nIpsum')


class TestNotesImportView(TodosViewTest):

    csrf_checks = False

    def test_get(self):
        response = self.app.get('/notes-import', user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = {
            'file': Upload('file.txt', b'Lorem\n----------\nIpsum', 'text/plain')
        }

        response = self.app.post('/notes-import', data, user=self.test_user)
        self.assertEqual(response.status_code, 302, response.content)
        result = list(Note.objects.order_by('text').values_list('text', flat=True))
        expected = ['Ipsum', 'Lorem']
        self.assertEqual(result, expected)

    def test_post_with_error(self):
        data = {
            'file': ''
        }

        response = self.app.post('/notes-import', data, user=self.test_user)
        self.assertEqual(response.status_code, 200, response.content)


class TestNotesExportView(TodosViewTest):

    def test_get(self):
        NoteFactory(text='Lorem')
        NoteFactory(text='Ipsum')
        response = self.app.get('/notes-export', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'Lorem\n----------\nIpsum')


class FilesImportTest(TodosViewTest):

    csrf_checks = False

    file_type = None

    model = None

    file_field = None

    def setUp(self):
        super().setUp()
        self.tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
        os.makedirs(self.tmp_dir, exist_ok=True)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmp_dir)

    def _get(self):
        response = self.app.get('/files/{}/import'.format(self.file_type), user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def _post(self, data, filenames, files, status_code=302):
        response = self.app.post('/files/{}/import'.format(self.file_type), data, user=self.test_user)
        self.assertEqual(response.status_code, status_code, response.content)

        for num, file in enumerate(filenames):
            pfile = self.model.objects.get(**{self.file_field: file})
            self.assertEqual(getattr(pfile, self.file_field).read(), files[num])


class TestFilesImportView(FileTestMixin, FilesImportTest):

    def test_get(self):
        self._get()

    def test_post(self):
        filenames = list(map(lambda id: str(id) + '.txt', [uuid.uuid4(), uuid.uuid4()]))

        with open(os.path.join(self.tmp_dir, filenames[0]), 'w') as fh:
            fh.write('Foo')
        with open(os.path.join(self.tmp_dir, filenames[1]), 'w') as fh:
            fh.write('Bar')

        fh = BytesIO()

        with ZipFile(fh, 'w') as outfile:
            outfile.write(os.path.join(self.tmp_dir, filenames[0]), filenames[0])
            outfile.write(os.path.join(self.tmp_dir, filenames[1]), filenames[1])
        fh.seek(0)

        data = {
            'file': Upload('file.zip', fh.read(), 'application/zip')
        }

        self._post(data, filenames, [b'Foo', b'Bar'])

    def test_post_with_error(self):
        data = {
            'file': ''
        }

        self._post(data, [], [], 200)


class TestImagesImportView(ImageTestMixin, FilesImportTest):

    def test_get(self):
        self._get()

    def test_post(self):
        filenames = list(map(lambda id: str(id) + '.png', [uuid.uuid4(), uuid.uuid4()]))
        images = [generate_image('foo').getvalue(), generate_image('bar').getvalue()]

        with open(os.path.join(self.tmp_dir, filenames[0]), 'wb') as fh:
            fh.write(images[0])
        with open(os.path.join(self.tmp_dir, filenames[1]), 'wb') as fh:
            fh.write(images[1])

        fh = BytesIO()

        with ZipFile(fh, 'w') as outfile:
            outfile.write(os.path.join(self.tmp_dir, filenames[0]), filenames[0])
            outfile.write(os.path.join(self.tmp_dir, filenames[1]), filenames[1])
        fh.seek(0)

        data = {
            'file': Upload('file.zip', fh.read(), 'application/zip')
        }

        self._post(data, filenames, images)

    def test_post_with_error(self):
        data = {
            'file': ''
        }

        self._post(data, [], [], 200)


class TestFilesExportView(TodosViewTest):

    def setUp(self):
        super().setUp()
        self.tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
        os.makedirs(self.tmp_dir, exist_ok=True)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.filenames = list(map(lambda id: str(id) + '.txt', [uuid.uuid4(), uuid.uuid4()]))
        PrivateFileFactory(file=ContentFile(b'Foo', name=cls.filenames[0]))
        PrivateFileFactory(file=ContentFile(b'Bar', name=cls.filenames[1]))

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmp_dir)

    def test_get(self):
        response = self.app.get('/files/file/export', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        fh = BytesIO(response.content)
        with ZipFile(fh, 'r') as infile:
            infile.extractall(self.tmp_dir)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, self.filenames[0])))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, self.filenames[1])))
        with open(os.path.join(self.tmp_dir, self.filenames[0]), 'r') as fh:
            content = fh.read()
            self.assertEqual(content, 'Foo')
        with open(os.path.join(self.tmp_dir, self.filenames[1]), 'r') as fh:
            content = fh.read()
            self.assertEqual(content, 'Bar')


class TestImagesExportView(TodosViewTest):

    def setUp(self):
        super().setUp()
        self.tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
        os.makedirs(self.tmp_dir, exist_ok=True)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.filenames = list(map(lambda id: str(id) + '.png', [uuid.uuid4(), uuid.uuid4()]))
        cls.images = [generate_image('foo'), generate_image('bar')]
        PrivateImageFactory(image=ImageFile(cls.images[0], name=cls.filenames[0]))
        PrivateImageFactory(image=ImageFile(cls.images[1], name=cls.filenames[1]))

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmp_dir)

    def test_get(self):
        response = self.app.get('/files/image/export', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        fh = BytesIO(response.content)
        with ZipFile(fh, 'r') as infile:
            infile.extractall(self.tmp_dir)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, self.filenames[0])))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, self.filenames[1])))
        with open(os.path.join(self.tmp_dir, self.filenames[0]), 'rb') as fh:
            content = ImageFile(fh).read()
            self.assertEqual(content, self.images[0].getvalue())
        with open(os.path.join(self.tmp_dir, self.filenames[1]), 'rb') as fh:
            content = ImageFile(fh).read()
            self.assertEqual(content, self.images[1].getvalue())


class TestWidgetListView(TodosViewTest):

    with_fixtures = True

    def test_get(self):
        response = self.app.get('/widgets/list', user=self.test_user)
        self.assertEqual(response.status_code, 200)


class TestWidgetSaveView(TodosViewTest):

    with_fixtures = True

    csrf_checks = False

    def test_post(self):
        widgets = Widget.objects.exclude(type=Widget.WIDGET_TYPE_EVENTS)
        data = {
            'widget': [widget.pk for widget in widgets]
        }
        response = self.app.post('/widgets/save', data, user=self.test_user)
        self.assertEqual(response.status_code, 302)
        widget = Widget.objects.get(type=Widget.WIDGET_TYPE_EVENTS)
        self.assertFalse(widget.is_enabled)


class TestEventCreateView(TodosViewTest):

    csrf_checks = False

    def test_get(self):
        response = self.app.get('/events/create?event_date=2020-11-20', user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = {
            'description': 'Pay bills',
            'time': '10:00'
        }
        response = self.app.post('/events/create?event_date=2020-11-20', data, user=self.test_user)
        self.assertEqual(response.status_code, 302)

        event = Event.objects.first()
        result = event.description
        expected = 'Pay bills'
        self.assertEqual(result, expected)

        result = event.datetime_localized.strftime('%d-%m-%Y %H:%M')
        expected = '20-11-2020 10:00'
        self.assertEqual(result, expected)

    def test_get_invalid_date(self):
        response = self.app.get('/events/create?event_date=2020-11-', user=self.test_user, expect_errors=True)
        self.assertEqual(response.status_code, 400)


class TestEventUpdateView(TodosViewTest):

    csrf_checks = False

    def setUp(self):
        super().setUp()
        self.event = EventFactory(
            description='Pay bills',
            datetime=datetime.datetime(2020, 11, 20, 10, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        )

    def test_get(self):
        response = self.app.get('/events/{}/update'.format(self.event.pk), user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = {
            'description': 'Pay the bills',
            'time': '11:00'
        }
        response = self.app.post('/events/{}/update'.format(self.event.pk), data, user=self.test_user)
        self.assertEqual(response.status_code, 302)

        event = Event.objects.first()
        result = event.description
        expected = 'Pay the bills'
        self.assertEqual(result, expected)

        result = event.datetime_localized.strftime('%d-%m-%Y %H:%M')
        expected = '20-11-2020 11:00'
        self.assertEqual(result, expected)

    def test_post_with_error(self):
        data = {
            'description': 'Pay the bills',
            'time': ''
        }
        response = self.app.post('/events/{}/update'.format(self.event.pk), data, user=self.test_user)
        self.assertEqual(response.status_code, 200)


class TestEventDeleteView(TodosViewTest):

    csrf_checks = False

    def setUp(self):
        super().setUp()
        self.event = EventFactory(
            description='Pay bills',
            datetime=datetime.datetime(2020, 11, 20, 10, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        )

    def test_post(self):
        response = self.app.post('/events/{}/delete'.format(self.event.pk), user=self.test_user)
        self.assertEqual(response.status_code, 302)

        result = Event.objects.filter(pk=self.event.pk).first()
        self.assertIsNone(result)


class TestCarouselView(TodosViewTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        images = [generate_image('foo'), generate_image('bar')]
        cls.images = [
            PrivateImageFactory(image=ImageFile(images[0], name='foo.png')),
            PrivateImageFactory(image=ImageFile(images[1], name='bar.png'))
        ]
        cls.images[0].created_at = datetime.datetime(2020, 11, 20, 10, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        cls.images[0].save()
        cls.images[1].created_at = datetime.datetime(2020, 11, 20, 11, 0, tzinfo=pytz.timezone(settings.TIME_ZONE))
        cls.images[1].save()

    def test_get(self):
        response = self.app.get('/carousel', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        doc = response.pyquery

        items = PyQuery(doc.find('.carousel-item'))

        item = PyQuery(items[0])
        result = item.attr('class')
        expected = 'carousel-item active'
        self.assertEqual(result, expected)

        img = PyQuery(item.find('img'))
        result = img.attr('src')
        self.assertIn('/bar', result)

        item = PyQuery(items[1])
        result = item.attr('class')
        expected = 'carousel-item'
        self.assertEqual(result, expected)

        img = PyQuery(item.find('img'))
        result = img.attr('src')
        self.assertIn('/foo', result)

    def test_get_with_image_id(self):
        response = self.app.get('/carousel?image_id={}'.format(self.images[0].pk), user=self.test_user)
        self.assertEqual(response.status_code, 200)
        doc = response.pyquery

        items = PyQuery(doc.find('.carousel-item'))

        item = PyQuery(items[0])
        result = item.attr('class')
        expected = 'carousel-item'
        self.assertEqual(result, expected)

        img = PyQuery(item.find('img'))
        result = img.attr('src')
        self.assertIn('/bar', result)

        item = PyQuery(items[1])
        result = item.attr('class')
        expected = 'carousel-item active'
        self.assertEqual(result, expected)

        img = PyQuery(item.find('img'))
        result = img.attr('src')
        self.assertIn('/foo', result)
