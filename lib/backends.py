from abc import ABC

from django.conf import settings
from ipware import get_client_ip


class AuthenticationBackend(ABC):

    def is_authenticated(self, request):
        raise NotImplementedError()


class UserAuthenticationBackend(AuthenticationBackend):

    def is_authenticated(self, request):
        return request.user.is_authenticated


class IPAuthenticationBackend(AuthenticationBackend):

    def is_authenticated(self, request):
        client_ip, _ = get_client_ip(request)
        return client_ip in settings.IP_WHITELIST
