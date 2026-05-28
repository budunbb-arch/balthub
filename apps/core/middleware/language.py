from django.utils import translation


class LanguageMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        lang = request.GET.get("lang")

        if lang not in ["ru", "en"]:
            lang = request.session.get("lang", "ru")

        request.session["lang"] = lang

        translation.activate(lang)

        request.LANGUAGE_CODE = lang

        response = self.get_response(request)

        translation.deactivate()

        return response