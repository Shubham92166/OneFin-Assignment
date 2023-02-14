#Django
from django.http import JsonResponse
from django.views.generic import View

class RequestCounterMiddleware:
    """Custom middle to handle the request count"""

    request_count = 0

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        RequestCounterMiddleware.request_count += 1
        response = self.get_response(request)
        return response
        
class RequestCountView(View):
    """Handles the request counter increment"""

    def get(self, request):
        return JsonResponse({'requests': RequestCounterMiddleware.request_count})


class RequestCountResetView(View):
    """Handles the reset of request counter"""

    def post(self, request):
        RequestCounterMiddleware.request_count = 0
        return JsonResponse({'message': 'request count reset successfully'})
