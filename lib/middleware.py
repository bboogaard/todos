from services.cron.factory import CronServiceFactory


class CronMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        CronServiceFactory.create_for_middleware().run()

        response = self.get_response(request)

        return response
