from unittest import mock

from django.core.cache import cache
from django.test.testcases import TestCase

from services.cron.models import Job


class CronTestCase(TestCase):

    frequency = 300

    job_name = 'job_test'

    def setUp(self):
        super().setUp()
        cache.clear()
        self.call_list = []
        self.patcher = mock.patch('services.cron.service.CronService.get_jobs', self.get_jobs)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def get_jobs(self):
        job = Job(self.job_name, self.job_test, self.frequency)
        job.last_run = cache.get(job.cache_key, 0)
        return [job]

    def job_test(self):
        self.call_list.append(1)

    def assertJobRun(self, count=1):
        self.assertEqual(sum(self.call_list), count)

    def assertJobNotRun(self):
        self.assertEqual(sum(self.call_list), 0)
