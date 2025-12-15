from django.contrib import admin
from django.urls import path, include
from letters import views_ui

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views_ui.login_view, name="login"),
    path("signup/", views_ui.signup, name="signup"),
    path("logout/", views_ui.logout_view, name="logout"),
    path("", include("letters.urls")),
]
