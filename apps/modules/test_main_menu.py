from django.test import RequestFactory, TestCase

from apps.core.models import Module
from apps.modules.admin import MainMenuItemForm
from apps.modules.main_menu import get_context, get_section_url_choices
from apps.modules.models import MainMenuItem


class MainMenuTests(TestCase):
    def setUp(self):
        self.module = Module.objects.create(
            name="Главное меню",
            type="main_menu",
            template="default/modules/main_menu.html",
            position="main_menu",
        )

    def test_context_returns_active_items_in_order_and_marks_current_section(self):
        MainMenuItem.objects.create(
            module=self.module,
            name="Контакты",
            type="link",
            url="/feedback/",
            range=2,
        )
        MainMenuItem.objects.create(
            module=self.module,
            name="Все ЖК",
            type="section",
            url="/estates/projects/",
            css_class="highlight-item",
            range=1,
        )
        MainMenuItem.objects.create(
            module=self.module,
            name="Скрытый пункт",
            type="link",
            url="/hidden/",
            range=0,
            is_active=False,
        )

        context = get_context(
            RequestFactory().get("/estates/projects/example/"),
            self.module,
        )

        self.assertEqual(
            [item["name"] for item in context["main_menu_items"]],
            ["Все ЖК", "Контакты"],
        )
        self.assertTrue(context["main_menu_items"][0]["is_current"])
        self.assertEqual(context["main_menu_items"][0]["css_class"], "highlight-item")
        self.assertFalse(context["main_menu_items"][1]["is_current"])

    def test_section_choices_include_static_routes_but_not_dynamic_detail_routes(self):
        choices = dict(get_section_url_choices())

        self.assertIn("/estates/projects/", choices)
        self.assertNotIn("/estates/projects/example/", choices)
        self.assertFalse(any("project_detail" in label for label in choices.values()))

    def test_form_accepts_a_selected_section(self):
        choices = get_section_url_choices()
        section_url = next(url for url, _ in choices if url == "/estates/projects/")
        form = MainMenuItemForm(data={
            "name": "Все ЖК",
            "type": "section",
            "section_url": section_url,
            "link_url": "",
            "css_class": "custom-menu-item",
            "is_active": "on",
            "range": "0",
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["url"], section_url)
        self.assertEqual(form.cleaned_data["css_class"], "custom-menu-item")

    def test_form_accepts_http_and_relative_links_but_rejects_other_schemes(self):
        for url in ("/feedback/", "https://example.com/contact/"):
            with self.subTest(url=url):
                form = MainMenuItemForm(data={
                    "name": "Ссылка",
                    "type": "link",
                    "section_url": "",
                    "link_url": url,
                    "is_active": "on",
                    "range": "0",
                })

                self.assertTrue(form.is_valid(), form.errors)
                self.assertEqual(form.cleaned_data["url"], url)

        unsafe_form = MainMenuItemForm(data={
            "name": "Небезопасная ссылка",
            "type": "link",
            "section_url": "",
            "link_url": "javascript:alert(1)",
            "is_active": "on",
            "range": "0",
        })

        self.assertFalse(unsafe_form.is_valid())
        self.assertIn("link_url", unsafe_form.errors)
