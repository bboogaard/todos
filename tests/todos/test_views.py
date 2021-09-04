from django_webtest import WebTest
from django.core.cache import cache

from todos.models import Note, Todo
from tests.todos.factories import TodoFactory, UserFactory


class TodosViewTest(WebTest):

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
