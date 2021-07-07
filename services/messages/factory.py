from services.messages.service import MessageService


class MessageServiceFactory:

    @classmethod
    def create(cls):
        return MessageService()
