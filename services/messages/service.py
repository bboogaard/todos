import logging
import sys
from abc import ABC

import messagebird
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


logger = logging.getLogger(__name__)


class MessageService(ABC):

    def __init__(self):
        self.client = messagebird.Client(settings.MESSAGEBIRD_ACCESS_KEY)
        self.test = settings.MESSAGEBIRD_ACCESS_KEY.startswith('test_')

    def send(self, message: str):
        if not settings.MESSAGEBIRD_RECIPIENTS:
            raise ImproperlyConfigured("No Messagebird recipients defined")

        if not self._can_send():
            sys.stdout.write("Not enough Messagebird credit left\n")
            logger.error("Not enough Messagebird credit left")

        try:
            self.client.message_create(
                settings.MESSAGEBIRD_FROM_NAME,
                settings.MESSAGEBIRD_RECIPIENTS,
                message
            )
        except messagebird.client.ErrorException as e:
            sys.stdout.write(str(e) + "\n")
            logger.error(str(e))

    def _can_send(self) -> bool:
        if self.test:
            return True

        try:
            balance = self.client.balance()
        except messagebird.client.ErrorException as e:
            logger.warning(str(e))
            return False

        if balance.amount is None:
            return False

        return balance.amount >= settings.MESSAGEBIRD_MIN_AMOUNT
