from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from leftover_food_api.views import (
    about,
    create_donation,
    donations_page,
    home,
    overview,
    register,
    request_food,
)

urlpatterns = [
    path("", home, name="home"),
    path("login/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
    path("about/", about, name="about"),
    path("overview/", overview, name="overview"),
    path("donations/", donations_page, name="donations"),
    path("donate/", create_donation, name="create-donation"),
    path("request-food/", request_food, name="request-food"),
]
