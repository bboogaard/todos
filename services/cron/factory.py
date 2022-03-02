from services.cron.logger import CronLogger, OutputLogger
from services.cron.service import CronService


class CronServiceFactory:

    @classmethod
    def create_for_middleware(cls):
        return CronService(CronLogger())

    @classmethod
    def create_for_view(cls):
        return CronService(OutputLogger())
