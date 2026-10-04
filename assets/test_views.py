from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from assets.models import Asset, AssetCategory, Location

User = get_user_model()


class AssetViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="strongpass123")
        self.client.login(username="manager", password="strongpass123")
        self.category = AssetCategory.objects.create(name="Machinery")
        self.location = Location.objects.create(name="Plant A", code="PL-A")

    def test_dashboard_access(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_asset_list_access(self):
        Asset.objects.create(
            name="Compressor",
            asset_tag="ASSET-100",
            category=self.category,
            location=self.location,
        )
        response = self.client.get(reverse("asset-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Compressor")
