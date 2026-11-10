# /opt/balthub/apps/modules/admin.py

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from urllib.parse import urlsplit

from .main_menu import get_section_url_choices
from .models import (
    FooterMenuItem,
    MainMenuItem,
    TagsMenu,
    TagsMenuItem,
    TagCollection,
    TagCollectionItem,
)


class MainMenuItemForm(forms.ModelForm):
    section_url = forms.ChoiceField(
        choices=[("", "— Выберите раздел —")],
        required=False,
        label="Раздел",
    )
    link_url = forms.CharField(
        required=False,
        label="URL ссылки",
        widget=forms.URLInput(attrs={"placeholder": "/раздел/ или https://example.com"}),
    )

    class Meta:
        model = MainMenuItem
        fields = ("name", "type", "css_class", "is_active", "range")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = get_section_url_choices()
        current_url = self.instance.url if self.instance.pk else ""
        if current_url and current_url not in {value for value, _ in choices}:
            choices.append((current_url, f"Текущий раздел — {current_url}"))
        self.fields["section_url"].choices = choices

        if not self.is_bound and current_url:
            if self.instance.type == "section":
                self.initial["section_url"] = current_url
            else:
                self.initial["link_url"] = current_url

    def clean(self):
        cleaned_data = super().clean()
        item_type = cleaned_data.get("type")

        if item_type == "section":
            url = cleaned_data.get("section_url")
            if not url:
                self.add_error("section_url", "Выберите раздел сайта.")
        elif item_type == "link":
            url = (cleaned_data.get("link_url") or "").strip()
            if not url:
                self.add_error("link_url", "Укажите URL ссылки.")
            else:
                try:
                    parsed_url = urlsplit(url)
                except ValueError:
                    parsed_url = None

                is_relative_path = url.startswith("/") and not url.startswith("//")
                is_web_url = (
                    parsed_url is not None
                    and parsed_url.scheme in {"http", "https"}
                    and bool(parsed_url.netloc)
                )
                if is_web_url:
                    try:
                        URLValidator(schemes=["http", "https"])(url)
                    except ValidationError as error:
                        self.add_error("link_url", error)
                elif not is_relative_path:
                    self.add_error(
                        "link_url",
                        "Укажите относительный путь от корня сайта или HTTP(S)-ссылку.",
                    )
        else:
            url = ""

        cleaned_data["url"] = url
        return cleaned_data

    def save(self, commit=True):
        self.instance.url = self.cleaned_data["url"]
        return super().save(commit=commit)

    class Media:
        js = ("admin/js/main_menu_item_form.js",)


class MainMenuItemInline(admin.TabularInline):
    model = MainMenuItem
    form = MainMenuItemForm
    extra = 1
    fields = (
        "name",
        "type",
        "section_url",
        "link_url",
        "css_class",
        "is_active",
        "range",
    )

@admin.register(FooterMenuItem)
class FooterMenuItemAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "order", "is_active", "module")
    list_filter = ("is_active", "module")
    search_fields = ("title", "url", "module__name")
    ordering = ("order", "id")


class TagsMenuItemInline(admin.TabularInline):
    model = TagsMenuItem
    extra = 1
    fields = ("tag", "order", "is_active")


class TagsMenuInline(admin.StackedInline):
    model = TagsMenu
    extra = 0
    max_num = 1
    inlines = [TagsMenuItemInline]
    exclude = ["module"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return bool(obj and obj.pk)


@admin.register(TagsMenu)
class TagsMenuAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    inlines = [TagsMenuItemInline]


class TagCollectionItemInline(admin.TabularInline):
    model = TagCollectionItem
    extra = 1
    fields = ("tag", "image", "description", "order", "is_active")


@admin.register(TagCollection)
class TagCollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "quantity", "random", "module")
    list_filter = ("random", "module")
    search_fields = ("title",)
    inlines = [TagCollectionItemInline]
