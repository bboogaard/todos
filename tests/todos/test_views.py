from django_webtest import WebTest
from django.core.management import call_command

from api.data.models import Note
from tests.services.cron.testcases import CronTestCase
from tests.todos.factories import EventFactory, NoteFactory, TodoFactory, UserFactory


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


class TestCarouselView(TodosViewTest):

    def test_get(self):
        response = self.app.get('/carousel', user=self.test_user)
        self.assertEqual(response.status_code, 200)


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
