from django.views import View
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone

from apps.estates.projects.models import Project
from apps.estates.houses.models import House
from apps.estates.flats.models import Flat
from apps.estates.developers.models import Developer
from apps.estates.tags.models import Tag
from apps.core.documents.models import Document


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

        urls.append({
            "loc": base_url + reverse("project_list"),
            "lastmod": timezone.now().date().isoformat(),
            "changefreq": "daily",
            "priority": "0.9",
        })

        urls.append({
            "loc": base_url + reverse("house_list"),
            "lastmod": timezone.now().date().isoformat(),
            "changefreq": "daily",
            "priority": "0.9",
        })

        urls.append({
            "loc": base_url + reverse("developer_list"),
            "lastmod": timezone.now().date().isoformat(),
            "changefreq": "weekly",
            "priority": "0.9",
        })

        urls.append({
            "loc": base_url + reverse("tags:tag_list"),
            "lastmod": timezone.now().date().isoformat(),
            "changefreq": "weekly",
            "priority": "0.8",
        })

        urls.append({
            "loc": base_url + reverse("documents"),
            "lastmod": timezone.now().date().isoformat(),
            "changefreq": "weekly",
            "priority": "0.7",
        })

        for project in Project.objects.active().only("slug", "published_at"):
            urls.append({
                "loc": base_url + reverse("project_detail", args=[project.slug]),
                "lastmod": project.published_at.date().isoformat() if project.published_at else timezone.now().date().isoformat(),
                "changefreq": "weekly",
                "priority": "0.8",
            })

        for house in House.objects.active().only("slug", "project__slug", "published_at"):
            urls.append({
                "loc": base_url + reverse("house_detail", args=[house.project.slug, house.slug]),
                "lastmod": house.published_at.date().isoformat() if house.published_at else timezone.now().date().isoformat(),
                "changefreq": "weekly",
                "priority": "0.7",
            })

        for flat in Flat.objects.active().only("slug", "house__project__slug", "house__slug", "published_at"):
            urls.append({
                "loc": base_url + reverse("flat_detail", args=[flat.house.project.slug, flat.house.slug, flat.slug]),
                "lastmod": flat.published_at.date().isoformat() if flat.published_at else timezone.now().date().isoformat(),
                "changefreq": "weekly",
                "priority": "0.6",
            })

        for developer in Developer.objects.active().only("slug", "published_at"):
            urls.append({
                "loc": base_url + reverse("developer_detail", args=[developer.slug]),
                "lastmod": developer.published_at.date().isoformat() if developer.published_at else timezone.now().date().isoformat(),
                "changefreq": "weekly",
                "priority": "0.7",
            })

        for tag in Tag.objects.all().only("slug", "published_at"):
            lastmod = tag.published_at
            if hasattr(lastmod, "date"):
                lastmod = lastmod.date()
            urls.append({
                "loc": base_url + reverse("tags:tag_detail", args=[tag.slug]),
                "lastmod": lastmod.isoformat() if lastmod else timezone.now().date().isoformat(),
                "changefreq": "weekly",
                "priority": "0.6",
            })

        for document in Document.objects.filter(document_public=True, document_status="released").only("document_date", "id"):
            lastmod = document.document_date
            if hasattr(lastmod, "date"):
                lastmod = lastmod.date()
            urls.append({
                "loc": base_url + reverse("document_detail", args=[document.id]),
                "lastmod": lastmod.isoformat() if lastmod else timezone.now().date().isoformat(),
                "changefreq": "monthly",
                "priority": "0.5",
            })

        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        for url in urls:
            xml.append("  <url>")
            xml.append(f"    <loc>{url['loc']}</loc>")
            xml.append(f"    <lastmod>{url.get('lastmod', timezone.now().date().isoformat())}</lastmod>")
            xml.append(f"    <changefreq>{url.get('changefreq', 'weekly')}</changefreq>")
            xml.append(f"    <priority>{url.get('priority', '0.5')}</priority>")
            xml.append("  </url>")

        xml.append("</urlset>")

        return HttpResponse("\n".join(xml), content_type="application/xml")
