from django.urls import path
from . import views_ui

urlpatterns = [
    path("", views_ui.login_view, name="login"), # cite: uploaded:urls.py
    path("signup/", views_ui.signup_view, name="signup"), # cite: uploaded:urls.py
    path("logout/", views_ui.logout_view, name="logout"), # cite: uploaded:urls.py

    path("dashboard/", views_ui.dashboard, name="dashboard"), # cite: uploaded:urls.py

    path("search/", views_ui.search_user, name="search_user"), # cite: uploaded:urls.py
    path("connect/<int:user_id>/", views_ui.send_connection, name="connect"), # cite: uploaded:urls.py
    path("accept/<int:conn_id>/", views_ui.accept_connection, name="accept"), # cite: uploaded:urls.py

    path("conversation/<int:user_id>/", views_ui.conversation, name="conversation"), # cite: uploaded:urls.py
    path("send/<int:user_id>/", views_ui.send_letter, name="send_letter"), # cite: uploaded:urls.py

    path("modify/<int:letter_id>/", views_ui.modify_letter, name="modify"), # cite: uploaded:urls.py
    path("approve/<int:mod_id>/", views_ui.approve_modification, name="approve"), # cite: uploaded:urls.py
]