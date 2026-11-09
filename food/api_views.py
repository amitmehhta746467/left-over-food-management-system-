from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Donation, FoodRequest, Pickup
from .serializers import DonationSerializer, FoodRequestSerializer, PickupSerializer


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.select_related("donor").all()
    serializer_class = DonationSerializer

    def perform_create(self, serializer):
        serializer.save(donor=self.request.user if self.request.user.is_authenticated else self._demo_user())

    def _demo_user(self):
        from django.contrib.auth.models import User
        user, _ = User.objects.get_or_create(username="demo_donor")
        return user


class FoodRequestViewSet(viewsets.ModelViewSet):
    queryset = FoodRequest.objects.select_related("requester", "donation").all()
    serializer_class = FoodRequestSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(requester=self.request.user)
        else:
            from django.contrib.auth.models import User
            user, _ = User.objects.get_or_create(username="demo_receiver")
            serializer.save(requester=user)


class PickupViewSet(viewsets.ModelViewSet):
    queryset = Pickup.objects.select_related("request", "request__donation").all()
    serializer_class = PickupSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def stats(request):
    donations = Donation.objects.all()
    return Response({
        "donations_posted": donations.count(),
        "donations_available": donations.filter(status="available").count(),
        "donations_collected": donations.filter(status="collected").count(),
        "servings_rescued": donations.filter(status="collected").aggregate(
            total=Sum("quantity")
        )["total"] or 0,
        "active_requests": FoodRequest.objects.filter(
            status__in=["pending", "approved"]
        ).count(),
        "active_pickups": Pickup.objects.filter(
            status__in=["scheduled", "picked_up"]
        ).count(),
        "updated_at": timezone.now(),
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def nearby_donations(request):
    city = request.query_params.get("city", "")
    qs = Donation.objects.filter(status="available")
    if city:
        qs = qs.filter(city__icontains=city)
    return Response(DonationSerializer(qs[:20], many=True, context={"request": request}).data)
