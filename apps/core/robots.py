from django.views import View
from django.http import HttpResponse


class RobotsView(View):

    def get(self, request):

        base_url = request.build_absolute_uri("/").rstrip("/")
        host = request.get_host()

        lines = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /api/",
            "",
            f"Host: {host}",
            "",
            f"Sitemap: {base_url}/sitemap.xml",
        ]

        return HttpResponse("\n".join(lines), content_type="text/plain")
