from django.core.management import call_command

from lib.middleware import schedule_job


@schedule_job(24 * 60 * 60)
def update_index():
    call_command('update_index', age=24)
