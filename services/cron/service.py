import datetime
import inspect
from typing import List

import pytz
from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import make_aware, now

from services.cron.decorators import cron_jobs
from services.cron.logger import BaseCronLogger
from services.cron.models import Job


class CronService:

    jobs: List[Job]

    logger: BaseCronLogger

    def __init__(self, logger: BaseCronLogger):
        self.logger = logger
        self.jobs = self.get_jobs()

    def run(self, job_name: str = None, force: bool = False):
        for job in self.jobs:
            if job_name and job_name != job.job_name:
                continue
            self.logger.info('Checking cron job {}'.format(job.job_name))
            next_run = job.last_run + job.frequency
            current_time = now().timestamp()
            if current_time >= next_run or force:
                if self.job_execute(job):
                    cache.set(job.cache_key, current_time, timeout=None)
                    next_run = current_time + job.frequency
            self.logger.info('Next run: {}'.format(make_aware(
                datetime.datetime.fromtimestamp(next_run),
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

    @staticmethod
    def get_jobs():
        jobs = []
        for func, frequency in cron_jobs:
            job_name = getattr(func, 'job_name', '{}.{}'.format(inspect.getmodule(func).__name__, func.__name__))
            job = Job(job_name=job_name, func=func, frequency=frequency)
            job.last_run = cache.get(job.cache_key, 0)
            jobs.append(job)
        return jobs
