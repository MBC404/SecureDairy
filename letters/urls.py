from django.urls import path
from . import views_ui

urlpatterns = [
    path("approve/<int:version_id>/", views_ui.approve_modification, name="approve_modification"),
    path("dashboard/", views_ui.dashboard, name="dashboard"),
    path("search/", views_ui.search_user, name="search_user"),
    path("connect/<int:user_id>/", views_ui.connect_user, name="connect"),
    path("accept/<int:conn_id>/", views_ui.accept_request, name="accept"),
    path("conversation/<int:user_id>/", views_ui.conversation, name="conversation"),
    path("send/<int:user_id>/", views_ui.send_letter, name="send_letter"),
    path("modify/<int:letter_id>/", views_ui.modify_letter, name="modify"),
]
