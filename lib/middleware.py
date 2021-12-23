import datetime
import inspect
import logging

import pytz
from django.conf import settings
from django.core.cache import cache
from django.utils.module_loading import autodiscover_modules
from django.utils.text import slugify
from django.utils.timezone import make_aware, now


logger = logging.getLogger(__name__)

cron_jobs = []


def schedule_job(frequency):

    def decorator(func):
        cron_jobs.append((func, frequency))

    return decorator


autodiscover_modules('cron')


class CronMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for func, frequency in cron_jobs:
            job_name = getattr(func, 'job_name', '{}.{}'.format(inspect.getmodule(func).__name__, func.__name__))
            logger.info('Checking cron job {}'.format(job_name))
            cache_key = 'cron-run-{}'.format(slugify(job_name))
            last_run = cache.get(cache_key, 0)
            next_run = last_run + frequency
            current_time = now().timestamp()
            if current_time >= next_run:
                logger.info('Cron triggered for job {}'.format(job_name))
                func()
                cache.set(cache_key, current_time, timeout=None)
                next_run = current_time + frequency
            logger.info('Next run: {}'.format(make_aware(
                datetime.datetime.fromtimestamp(next_run),
                pytz.timezone(settings.TIME_ZONE)
            )))

        response = self.get_response(request)

        return response
