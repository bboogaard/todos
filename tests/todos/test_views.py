from io import BytesIO

from django_webtest import WebTest
from django.core.cache import cache
from django.core.management import call_command
from PIL import Image
from webtest import Upload

from todos.models import Note, PrivateFile, Todo, Wallpaper
from todos.settings import cache_settings
from tests.todos.factories import NoteFactory, PrivateFileFactory, TodoFactory, UserFactory


class TodosViewTest(WebTest):

    with_fixtures = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if cls.with_fixtures:
            call_command('loaddata', 'wallpapers.json')
            call_command('collectmedia', '--noinput')

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_user = UserFactory()


class TestIndexView(TodosViewTest):

    def test_get(self):
        response = self.app.get('/', user=self.test_user)
        self.assertEqual(response.status_code, 200)


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
            'todos_position': 'bottom'
        }
        response = self.app.post('/settings-save', data, user=self.test_user)
        self.assertEqual(response.status_code, 302)

        settings = cache_settings.load()
        self.assertEqual(settings.todos_position, 'bottom')


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


class TestFileListView(TodosViewTest):

    def test_get(self):
        response = self.app.get('/files/list', user=self.test_user)
        self.assertEqual(response.status_code, 200)


class TestFileCreateView(TodosViewTest):

    csrf_checks = False

    def test_get(self):
        response = self.app.get('/files/create', user=self.test_user)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = {
            'file': Upload('file.txt', b'Foo', 'text/plain')
        }

        response = self.app.post('/files/create', data, user=self.test_user)
        self.assertEqual(response.status_code, 302, response.content)
        self.assertEqual(PrivateFile.objects.count(), 1)
        pfile = PrivateFile.objects.first()
        self.assertEqual(pfile.file.read(), b'Foo')

    def test_post_with_error(self):
        data = {
            'file': ''
        }

        response = self.app.post('/files/create', data, user=self.test_user)
        self.assertEqual(response.status_code, 200, response.content)


class TestFileDeleteView(TodosViewTest):

    csrf_checks = False

    def test_post(self):
        pfile = PrivateFileFactory()
        data = {
            'file': [pfile.pk]
        }

        response = self.app.post('/files/delete', data, user=self.test_user)
        self.assertEqual(response.status_code, 302, response.content)
        self.assertEqual(PrivateFile.objects.count(), 0)


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
