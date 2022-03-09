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

from todos.models import CodeSnippet, Event, HistoricalDate, Note, PrivateFile, PrivateImage, Todo, Wallpaper, Widget
from tests.services.cron.testcases import CronTestCase
from tests.todos.factories import CodeSnippetFactory, EventFactory, HistoricalDateFactory, NoteFactory, \
    PrivateFileFactory, PrivateImageFactory, TodoFactory, UserFactory
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


class FileDeleteTest(TodosViewTest):

    file_type = None

    model = None

    csrf_checks = False

    def _post(self, path, pk, status_code=200):
        response = self.app.post('/files/{}/{}/{}.json'.format(self.file_type, pk, path), user=self.test_user)
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(self.model.objects.filter(pk=pk).count(), 0)


class TestFileDeleteView(FileDeleteTest):

    file_type = 'file'

    model = PrivateFile

    def test_post(self):
        pfile = PrivateFileFactory()
        self._post('delete', pfile.pk)


class TestImageDeleteView(FileDeleteTest):

    file_type = 'image'

    model = PrivateImage

    def test_post(self):
        pfile = PrivateImageFactory()
        self._post('delete', pfile.pk)


class TestFileUploadView(TodosViewTest):

    csrf_checks = False

    def test_post_file(self):
        upload_file = b'Foo'
        data = {
            'file': Upload('file.txt', upload_file, 'text/plain')
        }

        response = self.app.post('/files/upload', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)
        pfile = PrivateFile.objects.first()
        self.assertEqual(pfile.file.read(), upload_file)

    def test_post_image(self):
        upload_file = generate_image().getvalue()
        data = {
            'file': Upload('foo.png', upload_file, 'image/png')
        }

        response = self.app.post('/files/upload', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)
        pfile = PrivateImage.objects.first()
        self.assertEqual(pfile.image.read(), upload_file)

    def test_post_with_error(self):
        response = self.app.post('/files/upload', {}, user=self.test_user, expect_errors=True)
        self.assertEqual(response.status_code, 400)


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


class TestFilesImportView(FilesImportTest):

    file_type = 'file'

    model = PrivateFile

    file_field = 'file'

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


class TestImagesImportView(FilesImportTest):

    file_type = 'image'

    model = PrivateImage

    file_field = 'image'

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

    csrf_checks = False

    with_fixtures = True

    def test_get(self):
        response = self.app.get('/widgets/list', user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = {
            'form-TOTAL_FORMS': ['5'],
            'form-INITIAL_FORMS': ['5'],
            'form-MIN_NUM_FORMS': ['0'],
            'form-MAX_NUM_FORMS': ['1000'],
            'form-0-is_enabled': ['on'],
            'form-0-id': ['1'],
            'form-0-refresh_interval': [''],
            'form-0-position': ['0'],
            'form-1-is_enabled': ['on'],
            'form-1-id': ['2'],
            'form-1-refresh_interval': [''],
            'form-1-position': ['1'],
            'form-2-is_enabled': ['on'],
            'form-2-id': ['3'],
            'form-2-refresh_interval': [''],
            'form-2-position': ['2'],
            'form-3-is_enabled': ['on'],
            'form-3-id': ['4'],
            'form-3-refresh_interval': ['120'],
            'form-3-position': ['3'],
            'form-4-is_enabled': ['on'],
            'form-4-id': ['5'],
            'form-4-refresh_interval': [''],
            'form-4-position': ['4'],
        }
        response = self.app.post('/widgets/list', data, user=self.test_user)
        self.assertEqual(response.status_code, 302)
        widget = Widget.objects.get(type=Widget.WIDGET_TYPE_EVENTS)
        self.assertEqual(widget.refresh_interval, 120)


class TestWidgetView(TodosViewTest):

    with_fixtures = True

    def test_get(self):
        widget = Widget.objects.get(type=Widget.WIDGET_TYPE_TODOS)
        response = self.app.get('/widgets/{}'.format(widget.pk), user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('Enter item', data['html'])


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


class TestDateListView(TodosViewTest):

    def test_get(self):
        response = self.app.get('/dates/list', user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def test_get_search(self):
        response = self.app.get('/dates/list?month=1', user=self.test_user)
        self.assertEqual(response.status_code, 200)


class TestDateCreateView(TodosViewTest):

    csrf_checks = False

    def test_get(self):
        response = self.app.get('/dates/create', user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = {
            'date': '10-05-1940',
            'event': 'German invasion'
        }
        response = self.app.post('/dates/create', data, user=self.test_user)
        self.assertEqual(response.status_code, 302)

        events = list(HistoricalDate.objects.filter(date=datetime.date(1940, 5, 10)).values_list('event', flat=True))
        self.assertIn('German invasion', events)

    def test_post_with_error(self):
        data = {
            'date': '10-05-1940',
            'event': ''
        }
        response = self.app.post('/dates/create', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)


class TestDateUpdateView(TodosViewTest):

    csrf_checks = False

    def setUp(self):
        super().setUp()
        self.date = HistoricalDateFactory(
            date=datetime.date(1940, 5, 10),
            event='German invasion'
        )

    def test_get(self):
        response = self.app.get('/dates/{}/update'.format(self.date.pk), user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = {
            'date': '10-05-1940',
            'event': 'Germans invaded'
        }
        response = self.app.post('/dates/{}/update'.format(self.date.pk), data, user=self.test_user)
        self.assertEqual(response.status_code, 302)

        date = HistoricalDate.objects.get(pk=self.date.pk)
        result = date.event
        expected = 'Germans invaded'
        self.assertEqual(result, expected)

    def test_post_with_error(self):
        data = {
            'date': '10-05-1940',
            'event': ''
        }
        response = self.app.post('/dates/{}/update'.format(self.date.pk), data, user=self.test_user)
        self.assertEqual(response.status_code, 200)


class TestDateDeleteView(TodosViewTest):

    csrf_checks = False

    def setUp(self):
        super().setUp()
        self.date = HistoricalDateFactory(
            date=datetime.date(1940, 5, 10),
            event='German invasion'
        )

    def test_post(self):
        response = self.app.post('/dates/delete', {'date': [self.date.pk]}, user=self.test_user)
        self.assertEqual(response.status_code, 302)

        result = HistoricalDate.objects.filter(pk=self.date.pk).first()
        self.assertIsNone(result)


class TestCronView(CronTestCase, TodosViewTest):

    frequency = 60 * 60

    job_name = 'cron_job'

    def test_get(self):
        response = self.app.get('/cron/cron_job', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        self.assertJobRun()

    def test_get_not_found(self):
        response = self.app.get('/cron/other_job', user=self.test_user, expect_errors=True)
        self.assertEqual(response.status_code, 404)


class TestCodeSnippetEditView(TodosViewTest):

    csrf_checks = False

    def test_get_default_new(self):
        response = self.app.get('/snippet/update', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        snippet = CodeSnippet.objects.first()
        self.assertIsNotNone(snippet)
        data = response.json
        self.assertIn('/snippet/update?object_id={}'.format(snippet.pk), data['html'])

    def test_get_default_first(self):
        snippet = CodeSnippetFactory(text='Lorem')
        response = self.app.get('/snippet/update', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('/snippet/update?object_id={}'.format(snippet.pk), data['html'])
        self.assertIn('Lorem', data['html'])

    def test_get_existing(self):
        snippet = CodeSnippetFactory(text='Lorem')
        response = self.app.get('/snippet/update?object_id={}'.format(snippet.pk), user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('/snippet/update?object_id={}'.format(snippet.pk), data['html'])
        self.assertIn('Lorem', data['html'])

    def test_post_save(self):
        snippet = CodeSnippetFactory(text='Lorem')
        response = self.app.post(
            '/snippet/update?object_id={}'.format(snippet.pk), {'text': 'Lorem ipsum'}, user=self.test_user
        )
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('/snippet/update?object_id={}'.format(snippet.pk), data['html'])
        self.assertIn('Lorem ipsum', data['html'])
        snippet.refresh_from_db()
        self.assertEqual(snippet.text, 'Lorem ipsum')

    def test_post_new(self):
        existing_snippet = CodeSnippetFactory(text='Lorem')
        response = self.app.post(
            '/snippet/update?action=new', {'text': ''}, user=self.test_user
        )
        self.assertEqual(response.status_code, 200)
        snippet = CodeSnippet.objects.last()
        self.assertEqual(snippet.position, existing_snippet.position + 1)
        data = response.json
        self.assertIn('/snippet/update?object_id={}'.format(snippet.pk), data['html'])

    def test_post_with_error(self):
        snippet = CodeSnippetFactory(text='Lorem')
        response = self.app.post(
            '/snippet/update?object_id={}'.format(snippet.pk), {}, user=self.test_user, expect_errors=True
        )
        self.assertEqual(response.status_code, 400)


class TestCodeSnippetDeleteView(TodosViewTest):

    csrf_checks = False

    def test_post_default_new(self):
        existing_snippet = CodeSnippetFactory(text='Lorem')
        response = self.app.post('/snippet/delete?object_id={}'.format(existing_snippet.pk), {}, user=self.test_user)
        self.assertEqual(response.status_code, 200)
        snippet = CodeSnippet.objects.filter(pk=existing_snippet.pk).first()
        self.assertIsNone(snippet)
        snippet = CodeSnippet.objects.first()
        self.assertIsNotNone(snippet)
        data = response.json
        self.assertIn('/snippet/update?object_id={}'.format(snippet.pk), data['html'])

    def test_post_previous(self):
        existing_snippet = CodeSnippetFactory(text='Lorem')
        delete_snippet = CodeSnippetFactory(text='Ipsum')
        response = self.app.post('/snippet/delete?object_id={}'.format(delete_snippet.pk), {}, user=self.test_user)
        self.assertEqual(response.status_code, 200)
        snippet = CodeSnippet.objects.filter(pk=delete_snippet.pk).first()
        self.assertIsNone(snippet)
        data = response.json
        self.assertIn('/snippet/update?object_id={}'.format(existing_snippet.pk), data['html'])

    def test_post_not_found(self):
        existing_snippet = CodeSnippetFactory(text='Lorem')
        response = self.app.post('/snippet/delete?object_id={}'.format(existing_snippet.pk + 1), {},
                                 user=self.test_user, expect_errors=True)
        self.assertEqual(response.status_code, 404)
