import datetime
import json

from django.utils.timezone import now

from api.data.models import CodeSnippet, Note, Todo
from tests.todos.factories import CodeSnippetFactory, NoteFactory, TodoFactory
from tests.todos.test_views import TodosViewTest


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
