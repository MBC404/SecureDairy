from django.urls import path
from . import views_ui

urlpatterns = [
    path("", views_ui.login_view, name="login"),
    path("signup/", views_ui.signup_view, name="signup"),
    path("logout/", views_ui.logout_view, name="logout"),

    path("dashboard/", views_ui.dashboard, name="dashboard"),

    path("search/", views_ui.search_user, name="search_user"),
    path("connect/<int:user_id>/", views_ui.send_connection, name="connect"),
    path("accept/<int:conn_id>/", views_ui.accept_connection, name="accept"),

    path("conversation/<int:user_id>/", views_ui.conversation, name="conversation"),
    path("send/<int:user_id>/", views_ui.send_letter, name="send_letter"),

    path("modify/<int:letter_id>/", views_ui.modify_letter, name="modify"),
    path("approve/<int:mod_id>/", views_ui.approve_modification, name="approve"),
]
