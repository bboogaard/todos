import datetime

from django.core.cache import cache
from django.utils.timezone import now

from services.cron.exceptions import JobNotFound
from services.cron.factory import CronServiceFactory
from tests.services.cron.testcases import CronTestCase


class TestCronService(CronTestCase):

    frequency = 60 * 60

    job_name = 'cron_job'

    def test_run(self):
        CronServiceFactory.create_for_middleware().run()
        self.assertJobRun()

    def test_run_skip(self):
        cache.set('cron-run-cron_job', (now() - datetime.timedelta(minutes=30)).timestamp())
        CronServiceFactory.create_for_middleware().run()
        self.assertJobNotRun()

    def test_run_job_name(self):
        CronServiceFactory.create_for_middleware().run('cron_job')
        self.assertJobRun()

    def test_run_job_name_not_found(self):
        with self.assertRaises(JobNotFound):
            CronServiceFactory.create_for_middleware().run('other_job')
        self.assertJobNotRun()

    def test_run_force(self):
        cache.set('cron-run-cron_job', (now() - datetime.timedelta(minutes=30)).timestamp())
        CronServiceFactory.create_for_middleware().run(force=True)
        self.assertJobRun()
