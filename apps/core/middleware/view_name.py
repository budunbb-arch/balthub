from django.urls import resolve


class ViewNameMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            resolver = resolve(request.path_info)
            request.view_name = resolver.url_name
        except Exception:
            request.view_name = None

        return self.get_response(request)
