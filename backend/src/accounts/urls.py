from django.urls import path

from accounts.apis import LoginApi, LogoutApi, MeApi, RegisterApi

urlpatterns = [
    path("register/", RegisterApi.as_view(), name="auth-register"),
    path("login/", LoginApi.as_view(), name="auth-login"),
    path("logout/", LogoutApi.as_view(), name="auth-logout"),
    path("me/", MeApi.as_view(), name="auth-me"),
]
