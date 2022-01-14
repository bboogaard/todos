import datetime
import inspect
from typing import List

import pytz
from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import make_aware, now

from services.cron.decorators import cron_jobs
from services.cron.exceptions import JobNotFound
from services.cron.logger import BaseCronLogger
from services.cron.models import Job


class CronService:

    jobs: List[Job]

    logger: BaseCronLogger

    def __init__(self, logger: BaseCronLogger):
        self.logger = logger
        self.jobs = self.get_jobs()

    def run(self, job_name: str = None, force: bool = False):
        current_time = now().timestamp()
        for job in self.get_jobs_to_run(current_time, job_name, force):
            if self.job_execute(job):
                cache.set(job.cache_key, current_time, timeout=None)
            self.logger.info('Next run: {}'.format(make_aware(
                datetime.datetime.fromtimestamp(job.next_run),
                pytz.timezone(settings.TIME_ZONE)
            )))

    def job_execute(self, job: Job):
        self.logger.info('Cron triggered for job {}'.format(job.job_name))
        try:
            job.func()
            return True
        except Exception as exc:
            self.logger.error('Error executing job {}: {}'.format(job.job_name, str(exc)))
            return False

    def get_jobs_to_run(self, time: float, job_name: str = None, force: bool = False):

        def _job_should_run(job: Job) -> bool:
            self.logger.info('Checking cron job {}'.format(job.job_name))
            if job_name and job.job_name != job_name:
                return False

            return time >= job.next_run or force

        job_names = [job.job_name for job in self.jobs]
        if job_name and job_name not in job_names:
            raise JobNotFound()

        return list(filter(_job_should_run, self.jobs))

    @staticmethod
    def get_jobs():
        jobs = []
        for func, frequency in cron_jobs:
            job_name = getattr(func, 'job_name', '{}.{}'.format(inspect.getmodule(func).__name__, func.__name__))
            job = Job(job_name=job_name, func=func, frequency=frequency)
            job.last_run = cache.get(job.cache_key, 0)
            jobs.append(job)
        return jobs
