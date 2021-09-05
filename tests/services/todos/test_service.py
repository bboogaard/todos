from django.core.files.base import ContentFile
from django.test.testcases import TestCase
from freezegun import freeze_time

from services.factory import ItemServiceFactory
from todos.models import Todo
from tests.todos.factories import TodoFactory


class TestTodoService(TestCase):

    def setUp(self):
        super().setUp()
        self.service = ItemServiceFactory.todos()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        TodoFactory(description='Pay bills')
        TodoFactory(description='Take out trash')
        TodoFactory(description='Dentist', status=Todo.INACTIVE_STATUS)

    def test_all(self):
        result = self.service.all()
        expected = ['Pay bills', 'Take out trash', 'Dentist']
        self.assertEqual(result, expected)

    def test_get_active(self):
        result = self.service.get_active()
        expected = ['Pay bills', 'Take out trash']
        self.assertEqual(result, expected)

    def test_search(self):
        result = self.service.search('Dent')
        expected = ['Dentist']
        self.assertEqual(result, expected)

    def test_save_new(self):
        self.service.save(['Pay bills', 'Take out trash', 'Call mom'])
        result = list(Todo.objects.order_by('description').values_list('description', flat=True))
        expected = ['Call mom', 'Dentist', 'Pay bills', 'Take out trash']
        self.assertEqual(result, expected)

    def test_save_activate(self):
        TodoFactory(description='Done', status=Todo.INACTIVE_STATUS)
        self.service.save(['Pay bills', 'Take out trash', 'Done'])
        todo = Todo.objects.get(description='Done')
        self.assertTrue(todo.is_active)

    def test_save_deactivate(self):
        self.service.save(['Pay bills'])
        todo = Todo.objects.get(description='Take out trash')
        self.assertFalse(todo.is_active)

    def test_activate(self):
        self.service.activate(['Dentist'])
        todo = Todo.objects.get(description='Dentist')
        self.assertTrue(todo.is_active)

    @freeze_time('27-04-2020')
    def test_upcoming(self):
        TodoFactory(description='Doctor 28-04-2020')
        TodoFactory(description='Job interview 07-05-2020')
        result = self.service.upcoming()
        expected = ['Doctor 28-04-2020']
        self.assertEqual(result, expected)

    def test_dump(self):
        fh = self.service.dump('todos.txt')
        result = fh.read()
        expected = 'Pay bills\nTake out trash'
        self.assertEqual(result, expected)

    def test_load(self):
        self.service.load(ContentFile(b'Doctor\nJob interview'))
        result = list(Todo.objects.order_by('description').values_list('description', flat=True))
        expected = ['Dentist', 'Doctor', 'Job interview', 'Pay bills', 'Take out trash']
        self.assertEqual(result, expected)
