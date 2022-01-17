import logging
from abc import ABC


logger = logging.getLogger(__name__)


class BaseCronLogger(ABC):

    def info(self, message: str):
        raise NotImplementedError()

    def warning(self, message: str):
        raise NotImplementedError()

    def error(self, message: str):
        raise NotImplementedError()

    def get_value(self):
        raise NotImplementedError()


class CronLogger(BaseCronLogger):

    def info(self, message: str):
        logger.info(message)

    def warning(self, message: str):
        logger.warning(message)

    def error(self, message: str):
        logger.error(message)

    def get_value(self):
        return ''


class OutputLogger(BaseCronLogger):

    def __init__(self):
        self.buffer = []

    def info(self, message: str):
        self._log('INFO', message)

    def warning(self, message: str):
        self._log('WARNING', message)

    def error(self, message: str):
        self._log('ERROR', message)

    def get_value(self):
        return '\n'.join(self.buffer)

    def _log(self, level: str, message: str):
        self.buffer.append('[{}] {}'.format(level, message))
