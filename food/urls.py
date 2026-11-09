from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import DonationViewSet, FoodRequestViewSet, PickupViewSet, stats, nearby_donations

router = DefaultRouter()
router.register("donations", DonationViewSet, basename="donation")
router.register("requests", FoodRequestViewSet, basename="request")
router.register("pickups", PickupViewSet, basename="pickup")

urlpatterns = [
    path("", include(router.urls)),
    path("stats/", stats, name="stats"),
    path("nearby-donations/", nearby_donations, name="nearby-donations"),
]
