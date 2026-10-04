from django.contrib import admin
from .models import Asset, AssetCategory, AssetAssignment, Location, MaintenanceRecord

admin.site.register(AssetCategory)
admin.site.register(Location)
admin.site.register(Asset)
admin.site.register(MaintenanceRecord)
admin.site.register(AssetAssignment)
