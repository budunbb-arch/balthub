from django.contrib import admin

from .models import AccountAccount, AccountAccountGroup, AccountGroup


class AccountAccountGroupInline(admin.TabularInline):
    model = AccountAccountGroup
    extra = 1


@admin.register(AccountGroup)
class AccountGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "employee",
        "client",
        "developer_contact",
        "blog_author",
        "blog_editor",
        "upload_files",
    )
    list_filter = (
        "employee",
        "client",
        "developer_contact",
        "blog_author",
        "blog_editor",
        "upload_files",
    )
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(AccountAccount)
class AccountAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "secret_idle")
    list_filter = ("active",)
    search_fields = ("name",)
    ordering = ("name",)
    inlines = (AccountAccountGroupInline,)
    exclude = ("password",)
