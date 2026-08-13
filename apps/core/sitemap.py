from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone

from apps.estates.projects.models import Project
from apps.estates.houses.models import House
from apps.estates.flats.models import Flat
from apps.estates.developers.models import Developer


from django.views import View
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone

from apps.estates.projects.models import Project
from apps.estates.houses.models import House
from apps.estates.flats.models import Flat
from apps.estates.developers.models import Developer


class SitemapView(View):

    def get(self, request):

        base_url = "https://balthub.rf39.ru"

        urls = []

        urls.append({
            "loc": base_url + "/",
            "lastmod": timezone.now().date().isoformat(),
            "changefreq": "daily",
            "priority": "1.0",
        })

        for project in Project.objects.active().only("slug", "updated_at"):
            urls.append({
                "loc": base_url + reverse("project_detail", args=[project.slug]),
                "lastmod": project.updated_at.date().isoformat() if project.updated_at else timezone.now().date().isoformat(),
                "changefreq": "weekly",
                "priority": "0.8",
            })

        for house in House.objects.active().only("slug", "project__slug", "updated_at"):
            urls.append({
                "loc": base_url + reverse("house_detail", args=[house.project.slug, house.slug]),
                "lastmod": house.updated_at.date().isoformat() if house.updated_at else timezone.now().date().isoformat(),
                "changefreq": "weekly",
                "priority": "0.7",
            })

        for flat in Flat.objects.active().only("slug", "house__project__slug", "house__slug", "updated_at"):
            urls.append({
                "loc": base_url + reverse("flat_detail", args=[flat.house.project.slug, flat.house.slug, flat.slug]),
                "lastmod": flat.updated_at.date().isoformat() if flat.updated_at else timezone.now().date().isoformat(),
                "changefreq": "weekly",
                "priority": "0.6",
            })

        for developer in Developer.objects.active().only("slug", "updated_at"):
            urls.append({
                "loc": base_url + reverse("developer_detail", args=[developer.slug]),
                "lastmod": developer.updated_at.date().isoformat() if developer.updated_at else timezone.now().date().isoformat(),
                "changefreq": "weekly",
                "priority": "0.7",
            })

        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        for url in urls:
            xml.append("  <url>")
            xml.append(f"    <loc>{url['loc']}</loc>")
            xml.append(f"    <lastmod>{url['lastmod']}</lastmod>")
            xml.append(f"    <changefreq>{url['changefreq']}</changefreq>")
            xml.append(f"    <priority>{url['priority']}</priority>")
            xml.append("  </url>")

        xml.append("</urlset>")

        return HttpResponse("\n".join(xml), content_type="application/xml")
