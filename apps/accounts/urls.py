from django.urls import path

from .views import (
    account_activate,
    account_dashboard,
    account_login,
    account_logout,
    account_password_reset,
    account_password_reset_request,
    account_profile_save,
    account_register,
)


urlpatterns = [
    path("", account_dashboard, name="account_dashboard"),
    path("profile/", account_profile_save, name="account_profile_save"),
    path("login/", account_login, name="account_login"),
    path("logout/", account_logout, name="account_logout"),
    path("password-reset/request/", account_password_reset_request, name="account_password_reset_request"),
    path("password-reset/<str:token>/", account_password_reset, name="account_password_reset"),
    path("register/", account_register, name="account_register"),
    path("activate/<str:token>/", account_activate, name="account_activate"),
]
