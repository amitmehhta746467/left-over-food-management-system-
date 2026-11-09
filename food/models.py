from django.db import models
from django.contrib.auth.models import User

class Donation(models.Model):
    FOOD_TYPES = [
        ("meal", "Meal"),
        ("rice", "Rice"),
        ("bread", "Bread"),
        ("vegetables", "Vegetables"),
        ("fruits", "Fruits"),
        ("bakery", "Bakery"),
        ("other", "Other"),
    ]
    STATUS = [
        ("available", "Available"),
        ("reserved", "Reserved"),
        ("collected", "Collected"),
        ("expired", "Expired"),
    ]

    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="donations")
    title = models.CharField(max_length=150)
    food_type = models.CharField(max_length=30, choices=FOOD_TYPES, default="meal")
    quantity = models.PositiveIntegerField(help_text="Number of servings")
    description = models.TextField(blank=True)
    pickup_address = models.CharField(max_length=255)
    city = models.CharField(max_length=80, default="Yamuna Nagar")
    prepared_at = models.DateTimeField()
    safe_until = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS, default="available")
    image = models.ImageField(upload_to="donations/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.quantity} servings"


class FoodRequest(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("fulfilled", "Fulfilled"),
        ("cancelled", "Cancelled"),
    ]
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="food_requests")
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name="requests")
    servings_requested = models.PositiveIntegerField()
    pickup_note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.id} - {self.donation.title}"


class Pickup(models.Model):
    STATUS = [
        ("scheduled", "Scheduled"),
        ("picked_up", "Picked Up"),
        ("delivered", "Delivered"),
    ]
    request = models.OneToOneField(FoodRequest, on_delete=models.CASCADE, related_name="pickup")
    pickup_time = models.DateTimeField()
    volunteer_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="scheduled")
    qr_code = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.qr_code = f"FOOD-{self.request_id or 'NEW'}-{self.id or 'X'}"
        super().save(*args, **kwargs)
