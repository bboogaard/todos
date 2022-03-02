from django.core.management import call_command

from services.cron.decorators import schedule_job


@schedule_job(24 * 60 * 60)
def update_index():
    call_command('update_index', age=24)


update_index.job_name = 'update_index'
