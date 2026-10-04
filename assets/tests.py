from django.test import TestCase

from .models import Asset, AssetCategory, Location


class AssetModelTests(TestCase):
    def test_asset_category_string(self):
        category = AssetCategory.objects.create(name="Machinery", description="Heavy equipment")
        self.assertEqual(str(category), "Machinery")

    def test_location_string(self):
        location = Location.objects.create(name="Plant A", code="PL-A", description="Main production area")
        self.assertEqual(str(location), "Plant A (PL-A)")

    def test_asset_creation(self):
        category = AssetCategory.objects.create(name="Generator")
        location = Location.objects.create(name="Warehouse", code="WH-1")
        asset = Asset.objects.create(
            name="Backup Generator",
            asset_tag="ASSET-001",
            manufacturer="Acme",
            model="G-100",
            category=category,
            location=location,
            status="available",
            condition="good",
        )
        self.assertEqual(str(asset), "Backup Generator (ASSET-001)")
