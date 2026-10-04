import os
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from assets.models import Asset, AssetCategory, Location


class Command(BaseCommand):
    help = "Seed sample asset management data for the application."

    def handle(self, *args, **options):
        if Asset.objects.exists():
            self.stdout.write(self.style.WARNING("Assets already exist. Skipping seed."))
            return

        category_machinery = AssetCategory.objects.create(
            name="Machinery",
            description="Production and industrial machinery",
        )
        category_electrical = AssetCategory.objects.create(
            name="Electrical",
            description="Electrical systems and equipment",
        )

        location_main = Location.objects.create(
            name="Plant A",
            code="PL-A",
            description="Main production floor",
        )
        location_warehouse = Location.objects.create(
            name="Warehouse B",
            code="WH-B",
            description="Inventory storage area",
        )

        Asset.objects.create(
            name="Hydraulic Press",
            asset_tag="AST-1001",
            serial_number="HP-2039",
            manufacturer="ForgeMax",
            model="FM-500",
            category=category_machinery,
            location=location_main,
            status="available",
            condition="good",
            purchase_date=timezone.now().date(),
            purchase_cost=18500.00,
            notes="Critical production asset.",
        )

        Asset.objects.create(
            name="Generator Set",
            asset_tag="AST-1002",
            serial_number="GEN-7742",
            manufacturer="PowerCore",
            model="PC-220",
            category=category_electrical,
            location=location_warehouse,
            status="maintenance",
            condition="fair",
            purchase_date=timezone.now().date(),
            purchase_cost=9200.00,
            notes="Scheduled preventive maintenance.",
        )

        self.stdout.write(self.style.SUCCESS("Sample asset data created successfully."))
