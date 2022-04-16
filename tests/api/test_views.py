import datetime
import json

from django.utils.timezone import now

from api.data.models import Todo
from tests.todos.factories import TodoFactory
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
