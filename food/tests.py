from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Donation


class WebsitePagesTests(TestCase):
    def setUp(self):
        self.donor = User.objects.create_user(username="test-donor")
        self.donation = Donation.objects.create(
            donor=self.donor,
            title="Fresh meal boxes",
            food_type="meal",
            quantity=12,
            pickup_address="10 Main Street",
            city="Yamuna Nagar",
            prepared_at=timezone.now(),
            safe_until=timezone.now() + timedelta(hours=3),
        )

    def test_primary_pages_render(self):
        for page in ("home", "about", "overview", "donations", "create-donation"):
            with self.subTest(page=page):
                response = self.client.get(reverse(page))
                self.assertEqual(response.status_code, 200)

    def test_donation_form_lists_food_types(self):
        response = self.client.get(reverse("create-donation"))

        self.assertContains(response, '<option value="meal">Meal</option>', html=True)
        self.assertContains(response, '<option value="vegetables">Vegetables</option>', html=True)

    def test_donation_search_filters_by_city_and_food_type(self):
        response = self.client.get(
            reverse("donations"),
            {"city": "Yamuna", "food_type": "meal"},
        )

        self.assertContains(response, self.donation.title)
        self.assertContains(response, "Yamuna Nagar")
        self.assertEqual(response.context["donations"].count(), 1)

    def test_donation_can_be_posted_from_the_form(self):
        response = self.client.post(reverse("create-donation"), {
            "name": "Community Kitchen",
            "title": "Vegetable meals",
            "food_type": "vegetables",
            "quantity": "20",
            "description": "Freshly prepared",
            "pickup_address": "22 Market Road",
            "city": "Yamuna Nagar",
            "prepared_at": "2026-11-09T12:00",
            "safe_until": "2026-11-09T18:00",
        })

        self.assertRedirects(response, reverse("donations"))
        self.assertTrue(Donation.objects.filter(title="Vegetable meals").exists())

    def test_donation_rejects_a_safe_until_time_before_preparation(self):
        response = self.client.post(reverse("create-donation"), {
            "name": "Community Kitchen",
            "title": "Unsafe time window",
            "food_type": "meal",
            "quantity": "10",
            "pickup_address": "22 Market Road",
            "city": "Yamuna Nagar",
            "prepared_at": "2026-11-09T18:00",
            "safe_until": "2026-11-09T12:00",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The safe-until time must be after the preparation time.")
        self.assertFalse(Donation.objects.filter(title="Unsafe time window").exists())

    def test_donation_rejects_invalid_datetime_input(self):
        response = self.client.post(reverse("create-donation"), {
            "name": "Community Kitchen",
            "title": "Invalid time",
            "food_type": "meal",
            "quantity": "10",
            "pickup_address": "22 Market Road",
            "city": "Yamuna Nagar",
            "prepared_at": "not-a-date",
            "safe_until": "2026-11-09T18:00",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter valid preparation and safe-until times.")


class AuthenticationTests(TestCase):
    def test_registration_creates_and_logs_in_user(self):
        response = self.client.post(reverse("register"), {
            "username": "new-member",
            "email": "member@example.com",
            "password1": "safe-test-password-2026",
            "password2": "safe-test-password-2026",
        })

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        user = User.objects.get(username="new-member")
        self.assertEqual(user.email, "member@example.com")

    def test_registration_rejects_duplicate_username(self):
        User.objects.create_user(username="existing-member", password="safe-test-password-2026")

        response = self.client.post(reverse("register"), {
            "username": "existing-member",
            "password1": "another-safe-password-2026",
            "password2": "another-safe-password-2026",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that username already exists.")
        self.assertEqual(User.objects.filter(username="existing-member").count(), 1)

    def test_login_and_logout(self):
        User.objects.create_user(username="member", password="safe-test-password-2026")

        response = self.client.post(reverse("login"), {
            "username": "member",
            "password": "safe-test-password-2026",
        })
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)
