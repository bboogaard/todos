import io
from contextlib import redirect_stdout

from django.core.management import call_command

from services.api import CronApi


class CronService(CronApi):

    available_commands = ['send_upcoming']

    def run(self, command: str) -> str:
        if command in self.available_commands:
            fh = io.StringIO()
            with redirect_stdout(fh):
                call_command(command)
            return fh.getvalue()
        return ''
