import datetime
import json
import os.path
import shutil
import uuid
from io import BytesIO
from zipfile import ZipFile

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.utils.timezone import make_aware, now, utc
from webtest import Upload

from api.data.models import CodeSnippet, Event, Note, PrivateFile, PrivateImage, Todo
from tests.todos.factories import CodeSnippetFactory, EventFactory, PrivateFileFactory, PrivateImageFactory, \
    NoteFactory, TodoFactory
from tests.todos.test_views import TodosViewTest
from tests.todos.utils import generate_image


class TestTodoViewSet(TodosViewTest):

    csrf_checks = False

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        current_time = now()
        cls.todos = [
            TodoFactory(description='Pay bills', activate_date=current_time - datetime.timedelta(days=1)),
            TodoFactory(description='Take out trash', activate_date=current_time - datetime.timedelta(days=2)),
            TodoFactory(
                description='Dentist',
                status=Todo.INACTIVE_STATUS,
                activate_date=current_time - datetime.timedelta(days=3)
            )
        ]

    def test_list(self):
        response = self.app.get('/api/v1/todos', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['description'] for item in data]
        expected = ['Pay bills', 'Take out trash']
        self.assertEqual(result, expected)

    def test_list_search(self):
        response = self.app.get('/api/v1/todos?search=Dent', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['description'] for item in data]
        expected = ['Dentist']
        self.assertEqual(result, expected)

    def test_create_many(self):
        data = [
            {
                'description': 'Do something'
            }
        ]
        response = self.app.post(
            '/api/v1/todos/create_many', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        todo = Todo.objects.filter(description='Do something').first()
        self.assertIsNotNone(todo)

    def test_update_many(self):
        data = [
            {
                'id': self.todos[0].pk,
                'description': 'Do something'
            }
        ]
        response = self.app.post(
            '/api/v1/todos/update_many', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        todo = Todo.objects.get(pk=self.todos[0].pk)
        self.assertEqual(todo.description, 'Do something')

    def test_delete_many(self):
        data = {
            'id': [self.todos[0].pk]
        }
        response = self.app.post(
            '/api/v1/todos/delete_many', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        todo = Todo.objects.get(pk=self.todos[0].pk)
        self.assertEqual(todo.status, Todo.INACTIVE_STATUS)

    def test_activate_many(self):
        todo = TodoFactory(description='Done', status=Todo.INACTIVE_STATUS)
        data = {
            'id': [todo.pk]
        }
        response = self.app.post(
            '/api/v1/todos/activate_many', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        todo.refresh_from_db()
        self.assertEqual(todo.status, Todo.ACTIVE_STATUS)


class TestTodosExport(TodosViewTest):

    csrf_checks = False

    def test_export_items(self):
        TodoFactory(description='Lorem', activate_date=make_aware(
            datetime.datetime(2022, 1, 2, 12, 0, 0),
            utc
        ))
        TodoFactory(description='Ipsum', activate_date=make_aware(
            datetime.datetime(2022, 1, 1, 12, 0, 0),
            utc
        ))
        data = {
            'filename': 'export.txt'
        }
        response = self.app.post('/api/v1/todos/export', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'{"description": "Lorem", "activate_date": "2022-01-02T12:00:00"}\n'
            b'{"description": "Ipsum", "activate_date": "2022-01-01T12:00:00"}'
        )

    def test_import_items(self):
        fh = b'{"description": "Lorem", "activate_date": "2022-01-02T12:00:00"}\n'\
             b'{"description": "Ipsum", "activate_date": "2022-01-01T12:00:00"}'
        data = {'file': Upload('file.txt', fh, 'text/plain')}

        response = self.app.post('/api/v1/todos/import', data, user=self.test_user)
        self.assertEqual(response.status_code, 200, response.content)
        result = list(Todo.objects.order_by('description').values_list('description', flat=True))
        expected = ['Ipsum', 'Lorem']
        self.assertEqual(result, expected)


class TestNoteViewSet(TodosViewTest):

    csrf_checks = False

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.notes = [
            NoteFactory(text='Pay bills', position=3),
            NoteFactory(text='Take out trash', position=2),
            NoteFactory(
                text='Dentist',
                status=Note.INACTIVE_STATUS,
                position=1
            )
        ]

    def test_list(self):
        response = self.app.get('/api/v1/notes', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['text'] for item in data['results']]
        expected = ['Pay bills']
        self.assertEqual(result, expected)

    def test_list_different_page(self):
        response = self.app.get('/api/v1/notes?page=2', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['text'] for item in data['results']]
        expected = ['Take out trash']
        self.assertEqual(result, expected)

    def test_list_search(self):
        response = self.app.get('/api/v1/notes?id={}'.format(self.notes[1].pk), user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['text'] for item in data['results']]
        expected = ['Take out trash']
        self.assertEqual(result, expected)

    def test_create_one(self):
        data = {
            'text': 'Do something'
        }
        response = self.app.post(
            '/api/v1/notes/create_one', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        note = Note.objects.filter(text='Do something').first()
        self.assertIsNotNone(note)

    def test_update_one(self):
        data = {
            'id': self.notes[0].pk,
            'text': 'Do something'
        }
        response = self.app.post(
            '/api/v1/notes/update_one', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        note = Note.objects.get(pk=self.notes[0].pk)
        self.assertEqual(note.text, 'Do something')

    def test_delete_one(self):
        data = {
            'id': self.notes[0].pk
        }
        response = self.app.post(
            '/api/v1/notes/delete_one', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        note = Note.objects.get(pk=self.notes[0].pk)
        self.assertEqual(note.status, Note.INACTIVE_STATUS)


class TestNotesExport(TodosViewTest):

    csrf_checks = False

    def test_export_items(self):
        NoteFactory(text='Lorem')
        NoteFactory(text='Ipsum')
        data = {
            'filename': 'export.txt'
        }
        response = self.app.post('/api/v1/notes/export', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)
        fh = b'{"text": "Ipsum", "position": 2}\n{"text": "Lorem", "position": 1}'
        self.assertEqual(response.content, fh)

    def test_import_items(self):
        fh = b'{"text": "Lorem", "position": 1}\n{"text": "Ipsum", "position": 2}'
        data = {'file': Upload('file.txt', fh, 'text/plain')}

        response = self.app.post('/api/v1/notes/import', data, user=self.test_user)
        self.assertEqual(response.status_code, 200, response.content)
        result = list(Note.objects.order_by('text').values_list('text', flat=True))
        expected = ['Ipsum', 'Lorem']
        self.assertEqual(result, expected)


class TestCodeSnippetViewSet(TodosViewTest):

    csrf_checks = False

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.snippets = [
            CodeSnippetFactory(text='Pay bills', position=3),
            CodeSnippetFactory(text='Take out trash', position=2),
            CodeSnippetFactory(text='Dentist', position=1)
        ]

    def test_list(self):
        response = self.app.get('/api/v1/snippets', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['text'] for item in data['results']]
        expected = ['Pay bills']
        self.assertEqual(result, expected)

    def test_list_different_page(self):
        response = self.app.get('/api/v1/snippets?page=2', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['text'] for item in data['results']]
        expected = ['Take out trash']
        self.assertEqual(result, expected)

    def test_create_one(self):
        data = {
            'text': 'Do something'
        }
        response = self.app.post(
            '/api/v1/snippets/create_one', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        snippet = CodeSnippet.objects.filter(text='Do something').first()
        self.assertIsNotNone(snippet)

    def test_update_one(self):
        data = {
            'id': self.snippets[0].pk,
            'text': 'Do something'
        }
        response = self.app.post(
            '/api/v1/snippets/update_one', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        snippet = CodeSnippet.objects.get(pk=self.snippets[0].pk)
        self.assertEqual(snippet.text, 'Do something')

    def test_delete_one(self):
        data = {
            'id': self.snippets[0].pk
        }
        response = self.app.post(
            '/api/v1/snippets/delete_one', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        snippet = CodeSnippet.objects.filter(pk=self.snippets[0].pk).first()
        self.assertIsNone(snippet)


class TestCodeSnippetExport(TodosViewTest):

    csrf_checks = False

    def test_export_items(self):
        CodeSnippetFactory(text='Lorem')
        CodeSnippetFactory(text='Ipsum')
        data = {
            'filename': 'export.txt'
        }
        response = self.app.post('/api/v1/snippets/export', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)
        fh = b'{"text": "Ipsum", "position": 2}\n{"text": "Lorem", "position": 1}'
        self.assertEqual(response.content, fh)

    def test_import_items(self):
        fh = b'{"text": "Lorem", "position": 1}\n{"text": "Ipsum", "position": 2}'
        data = {'file': Upload('file.txt', fh, 'text/plain')}

        response = self.app.post('/api/v1/snippets/import', data, user=self.test_user)
        self.assertEqual(response.status_code, 200, response.content)
        result = list(CodeSnippet.objects.order_by('text').values_list('text', flat=True))
        expected = ['Ipsum', 'Lorem']
        self.assertEqual(result, expected)


class TestFileViewSet(TodosViewTest):

    csrf_checks = False

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.files = [
            PrivateFileFactory(file=ContentFile(b'Foo', name='foo.txt')),
            PrivateFileFactory(file=ContentFile(b'Bar', name='bar.txt')),
        ]

    def test_list(self):
        response = self.app.get('/api/v1/files', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['id'] for item in data]
        expected = [self.files[1].pk, self.files[0].pk]
        self.assertEqual(result, expected)

    def test_list_search(self):
        response = self.app.get('/api/v1/files?id={}'.format(self.files[0].pk), user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['id'] for item in data]
        expected = [self.files[0].pk]
        self.assertEqual(result, expected)

    def test_delete_one(self):
        data = {
            'id': self.files[0].pk
        }
        response = self.app.post(
            '/api/v1/files/delete_one', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        file = PrivateFile.objects.filter(pk=self.files[0].pk).first()
        self.assertIsNone(file)


class TestFileExport(TodosViewTest):

    csrf_checks = False

    def setUp(self):
        super().setUp()
        self.filenames = list(map(lambda id: str(id) + '.txt', [uuid.uuid4(), uuid.uuid4()]))
        self.tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
        os.makedirs(self.tmp_dir, exist_ok=True)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmp_dir)

    def test_export_files(self):
        PrivateFileFactory(file=ContentFile(b'Baz', name=self.filenames[0]))
        PrivateFileFactory(file=ContentFile(b'Qux', name=self.filenames[1]))
        data = {
            'filename': 'export.zip'
        }
        response = self.app.post('/api/v1/files/export', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)

        fh = BytesIO(response.content)
        with ZipFile(fh, 'r') as infile:
            infile.extractall(self.tmp_dir)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, self.filenames[0])))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, self.filenames[1])))
        with open(os.path.join(self.tmp_dir, self.filenames[0]), 'r') as fh:
            content = fh.read()
            self.assertEqual(content, 'Baz')
        with open(os.path.join(self.tmp_dir, self.filenames[1]), 'r') as fh:
            content = fh.read()
            self.assertEqual(content, 'Qux')

    def test_import_files(self):
        with open(os.path.join(self.tmp_dir, self.filenames[0]), 'w') as fh:
            fh.write('Baz')
        with open(os.path.join(self.tmp_dir, self.filenames[1]), 'w') as fh:
            fh.write('Qux')

        fh = BytesIO()

        with ZipFile(fh, 'w') as outfile:
            outfile.write(os.path.join(self.tmp_dir, self.filenames[0]), self.filenames[0])
            outfile.write(os.path.join(self.tmp_dir, self.filenames[1]), self.filenames[1])
        fh.seek(0)

        data = {
            'file': Upload('file.zip', fh.read(), 'application/zip')
        }
        response = self.app.post('/api/v1/files/import', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)

        files = [b'Baz', b'Qux']
        for num, file in enumerate(self.filenames):
            pfile = PrivateFile.objects.get(file=file)
            self.assertEqual(pfile.file.read(), files[num])


class TestImageViewSet(TodosViewTest):

    csrf_checks = False

    def setUp(self):
        super().setUp()
        self.images = [
            PrivateImageFactory(image=ImageFile(generate_image(), name='foo.png')),
            PrivateImageFactory(image=ImageFile(generate_image(), name='bar.png')),
        ]

    def test_list(self):
        response = self.app.get('/api/v1/images', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['id'] for item in data]
        expected = [self.images[1].pk, self.images[0].pk]
        self.assertEqual(result, expected)

    def test_list_search(self):
        response = self.app.get('/api/v1/images?id={}'.format(self.images[0].pk), user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['id'] for item in data]
        expected = [self.images[0].pk]
        self.assertEqual(result, expected)

    def test_delete_one(self):
        data = {
            'id': self.images[0].pk
        }
        response = self.app.post(
            '/api/v1/images/delete_one', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        image = PrivateImage.objects.filter(pk=self.images[0].pk).first()
        self.assertIsNone(image)


class TestImageExport(TodosViewTest):

    csrf_checks = False

    def setUp(self):
        super().setUp()
        self.filenames = list(map(lambda id: str(id) + '.png', [uuid.uuid4(), uuid.uuid4()]))
        self.tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
        os.makedirs(self.tmp_dir, exist_ok=True)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmp_dir)

    def test_export_files(self):
        images = [generate_image('foo'), generate_image('bar')]
        PrivateImageFactory(image=ImageFile(images[0], name=self.filenames[0]))
        PrivateImageFactory(image=ImageFile(images[1], name=self.filenames[1]))

        data = {
            'filename': 'export.zip'
        }
        response = self.app.post('/api/v1/images/export', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)

        fh = BytesIO(response.content)
        with ZipFile(fh, 'r') as infile:
            infile.extractall(self.tmp_dir)
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, self.filenames[0])))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, self.filenames[1])))
        with open(os.path.join(self.tmp_dir, self.filenames[0]), 'rb') as fh:
            content = ImageFile(fh).read()
            self.assertEqual(content, images[0].getvalue())
        with open(os.path.join(self.tmp_dir, self.filenames[1]), 'rb') as fh:
            content = ImageFile(fh).read()
            self.assertEqual(content, images[1].getvalue())

    def test_import_files(self):
        images = [generate_image('foo').getvalue(), generate_image('bar').getvalue()]
        with open(os.path.join(self.tmp_dir, self.filenames[0]), 'wb') as fh:
            fh.write(images[0])
        with open(os.path.join(self.tmp_dir, self.filenames[1]), 'wb') as fh:
            fh.write(images[1])

        fh = BytesIO()

        with ZipFile(fh, 'w') as outfile:
            outfile.write(os.path.join(self.tmp_dir, self.filenames[0]), self.filenames[0])
            outfile.write(os.path.join(self.tmp_dir, self.filenames[1]), self.filenames[1])
        fh.seek(0)

        data = {
            'file': Upload('file.zip', fh.read(), 'application/zip')
        }
        response = self.app.post('/api/v1/images/import', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)

        for num, file in enumerate(self.filenames):
            pfile = PrivateImage.objects.get(image=file)
            self.assertEqual(pfile.image.read(), images[num])


class TestCarouselViewSet(TodosViewTest):

    def setUp(self):
        super().setUp()
        self.images = [
            PrivateImageFactory(image=ImageFile(generate_image(), name='foo.png')),
            PrivateImageFactory(image=ImageFile(generate_image(), name='bar.png')),
        ]

    def test_list(self):
        response = self.app.get('/api/v1/carousel', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['id'] for item in data['results']]
        expected = [self.images[1].pk]
        self.assertEqual(result, expected)

    def test_list_different_page(self):
        response = self.app.get('/api/v1/carousel?page=2', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['id'] for item in data['results']]
        expected = [self.images[0].pk]
        self.assertEqual(result, expected)

    def test_find_page(self):
        response = self.app.get('/api/v1/carousel/find_page?id={}'.format(self.images[0].pk), user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = data.get('page')
        expected = 2
        self.assertEqual(result, expected)

    def test_find_page_default_page(self):
        response = self.app.get('/api/v1/carousel/find_page', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = data.get('page')
        expected = 1
        self.assertEqual(result, expected)


class TestUploadViewSet(TodosViewTest):

    csrf_checks = False

    def test_upload_one(self):
        upload_file = b'Foo'
        data = {
            'file': Upload('file.txt', upload_file, 'text/plain')
        }

        response = self.app.post(
            '/api/v1/upload/upload_one', data, user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        pfile = PrivateFile.objects.first()
        self.assertEqual(pfile.file.read(), upload_file)


class TestEventViewSet(TodosViewTest):

    csrf_checks = False

    def setUp(self):
        super().setUp()
        self.events = [
            EventFactory(description='Lorem', datetime=make_aware(
                datetime.datetime(2022, 2, 1, 12, 0, 0),
                utc
            )),
            EventFactory(description='Ipsum', datetime=make_aware(
                datetime.datetime(2022, 1, 1, 12, 0, 0),
                utc
            ))
        ]

    def test_list(self):
        response = self.app.get('/api/v1/events', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['id'] for item in data]
        expected = [self.events[1].pk, self.events[0].pk]
        self.assertEqual(result, expected)

    def test_list_search(self):
        response = self.app.get('/api/v1/events?date_range=2022-01-01,2022-01-31', user=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json
        result = [item['id'] for item in data]
        expected = [self.events[1].pk]
        self.assertEqual(result, expected)

    def test_create_one(self):
        data = {
            'description': 'Dolor',
            'date': '2022-03-01',
            'time': '12:00:00'
        }
        response = self.app.post(
            '/api/v1/events/create_one', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json
        event = Event.objects.get(pk=data['id'])
        self.assertEqual(event.event_date, (1, 3))

    def test_update_one(self):
        data = {
            'id': self.events[1].pk,
            'description': 'Ipsum Dolor',
            'date': '2022-01-01',
            'time': '12:00:00'
        }
        response = self.app.post(
            '/api/v1/events/update_one', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.events[1].refresh_from_db()
        self.assertEqual(self.events[1].description, 'Ipsum Dolor')

    def test_delete_one(self):
        data = {
            'id': self.events[0].pk
        }
        response = self.app.post(
            '/api/v1/events/delete_one', json.dumps(data), user=self.test_user,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        event = Event.objects.filter(pk=self.events[0].pk).first()
        self.assertIsNone(event)

    def test_weeks(self):
        response = self.app.get(
            '/api/v1/events/weeks?year=2022&month=11', user=self.test_user
        )
        self.assertEqual(response.status_code, 200)


class TestEventsExport(TodosViewTest):

    csrf_checks = False

    def test_export_items(self):
        EventFactory(description='Lorem', datetime=make_aware(
            datetime.datetime(2022, 1, 2, 12, 0, 0),
            utc
        ))
        EventFactory(description='Ipsum', datetime=make_aware(
            datetime.datetime(2022, 1, 1, 12, 0, 0),
            utc
        ))
        data = {
            'filename': 'export.txt'
        }
        response = self.app.post('/api/v1/events/export', data, user=self.test_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'{"description": "Ipsum", "datetime": "2022-01-01T12:00:00"}\n'
            b'{"description": "Lorem", "datetime": "2022-01-02T12:00:00"}'
        )

    def test_import_items(self):
        fh = b'{"description": "Lorem", "datetime": "2022-01-02T12:00:00"}\n'\
             b'{"description": "Ipsum", "datetime": "2022-01-01T12:00:00"}'
        data = {'file': Upload('file.txt', fh, 'text/plain')}

        response = self.app.post('/api/v1/events/import', data, user=self.test_user)
        self.assertEqual(response.status_code, 200, response.content)
        result = list(Event.objects.order_by('description').values_list('description', flat=True))
        expected = ['Ipsum', 'Lorem']
        self.assertEqual(result, expected)
