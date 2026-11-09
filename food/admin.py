from django.contrib import admin
from .models import Donation, FoodRequest, Pickup

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("title", "food_type", "quantity", "city", "status", "safe_until", "created_at")
    list_filter = ("status", "food_type", "city")
    search_fields = ("title", "pickup_address", "city")

@admin.register(FoodRequest)
class FoodRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "donation", "requester", "servings_requested", "status", "created_at")
    list_filter = ("status",)

@admin.register(Pickup)
class PickupAdmin(admin.ModelAdmin):
    list_display = ("id", "request", "pickup_time", "volunteer_name", "status", "qr_code")
    list_filter = ("status",)
