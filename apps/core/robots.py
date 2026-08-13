from django.views import View
from django.http import HttpResponse


class RobotsView(View):

    def get(self, request):

        lines = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /api/",
            "",
            "Host: https://balthub.rf39.ru",
            "",
            "Sitemap: https://balthub.rf39.ru/sitemap.xml",
        ]

        return HttpResponse("\n".join(lines), content_type="text/plain")
