from django_webtest import WebTest
from django.core.management import call_command

from api.data.models import Note
from todos.models import Widget
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
