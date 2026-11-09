from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from food.models import Donation, FoodRequest


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user)
        messages.success(request, "Your account has been created.")
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})


def parse_local_datetime(value):
    parsed = parse_datetime(value)
    if parsed is not None and timezone.is_naive(parsed):
        return timezone.make_aware(parsed)
    return parsed


def impact_stats():
    donation_totals = Donation.objects.aggregate(
        donations=Count("id"),
        servings=Sum("quantity"),
    )
    return {
        "donations": donation_totals["donations"],
        "servings": donation_totals["servings"] or 0,
        "available": Donation.objects.filter(status="available").count(),
        "requests": FoodRequest.objects.count(),
    }


def home(request):
    donations = Donation.objects.filter(status="available")[:8]
    return render(request, "home.html", {
        "donations": donations,
        "stats": impact_stats(),
    })


def about(request):
    return render(request, "about.html")


def overview(request):
    counts = {
        item["food_type"]: item
        for item in Donation.objects.values("food_type").annotate(
            listings=Count("id"),
            servings=Sum("quantity"),
        )
    }
    categories = [
        {
            "value": value,
            "label": label,
            "listings": counts.get(value, {}).get("listings", 0),
            "servings": counts.get(value, {}).get("servings", 0) or 0,
        }
        for value, label in Donation.FOOD_TYPES
    ]
    return render(request, "overview.html", {
        "stats": impact_stats(),
        "categories": categories,
    })

def donations_page(request):
    donations = Donation.objects.filter(status="available")
    city = request.GET.get("city", "")
    food_type = request.GET.get("food_type", "")
    if city:
        donations = donations.filter(city__icontains=city)
    if food_type in dict(Donation.FOOD_TYPES):
        donations = donations.filter(food_type=food_type)
    return render(request, "donations.html", {
        "donations": donations,
        "city": city,
        "food_type": food_type,
        "food_types": Donation.FOOD_TYPES,
    })

def create_donation(request):
    if request.method == "POST":
        prepared_at = parse_local_datetime(request.POST.get("prepared_at", ""))
        safe_until = parse_local_datetime(request.POST.get("safe_until", ""))
        if prepared_at is None or safe_until is None:
            messages.error(request, "Enter valid preparation and safe-until times.")
            return render(request, "donate.html", {"food_types": Donation.FOOD_TYPES})
        if safe_until <= prepared_at:
            messages.error(request, "The safe-until time must be after the preparation time.")
            return render(request, "donate.html", {"food_types": Donation.FOOD_TYPES})

        user, _ = User.objects.get_or_create(username=request.POST.get("name", "demo_donor")[:150])
        Donation.objects.create(
            donor=user,
            title=request.POST["title"],
            food_type=request.POST["food_type"],
            quantity=request.POST["quantity"],
            description=request.POST.get("description", ""),
            pickup_address=request.POST["pickup_address"],
            city=request.POST.get("city", "Yamuna Nagar"),
            prepared_at=prepared_at,
            safe_until=safe_until,
        )
        messages.success(request, "Donation posted successfully.")
        return redirect("donations")
    return render(request, "donate.html", {"food_types": Donation.FOOD_TYPES})

def request_food(request):
    if request.method == "POST":
        donation = get_object_or_404(Donation, id=request.POST["donation_id"], status="available")
        user, _ = User.objects.get_or_create(username=request.POST.get("name", "demo_receiver")[:150])
        FoodRequest.objects.create(
            requester=user,
            donation=donation,
            servings_requested=request.POST["servings_requested"],
            pickup_note=request.POST.get("pickup_note", ""),
        )
        donation.status = "reserved"
        donation.save(update_fields=["status"])
        messages.success(request, "Food request submitted.")
        return redirect("donations")
    donations = Donation.objects.filter(status="available")
    return render(request, "request_food.html", {"donations": donations})
