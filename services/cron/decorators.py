from django.utils.module_loading import autodiscover_modules


cron_jobs = []


def schedule_job(frequency):

    def decorator(func):
        cron_jobs.append((func, frequency))

        return func

    return decorator


autodiscover_modules('cron')
