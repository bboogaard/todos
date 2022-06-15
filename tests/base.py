from django_webtest import WebTest
from django.core.management import call_command

from tests.api.factories import UserFactory


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
