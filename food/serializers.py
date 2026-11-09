from rest_framework import serializers
from .models import Donation, FoodRequest, Pickup

class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source="donor.username", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = "__all__"
        read_only_fields = ["donor", "created_at", "updated_at", "image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


class FoodRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source="requester.username", read_only=True)

    class Meta:
        model = FoodRequest
        fields = "__all__"
        read_only_fields = ["requester", "created_at"]


class PickupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pickup
        fields = "__all__"
