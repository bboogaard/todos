from typing import Callable

from dataclasses import dataclass, field
from django.utils.text import slugify


@dataclass
class Job:
    job_name: str
    func: Callable
    frequency: int
    last_run: int = field(init=False)

    @property
    def cache_key(self):
        return 'cron-run-{}'.format(slugify(self.job_name))

    @property
    def next_run(self):
        return self.last_run + self.frequency
