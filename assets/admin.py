from django.contrib import admin
from .models import Asset, AssetCategory, Location, MaintenanceRecord, MaintenanceSchedule, AssetAssignment, Department, Employee, AuditLog


class AssetInline(admin.TabularInline):
    model = Asset
    extra = 0
    fields = ["name", "asset_tag", "status", "condition"]


class MaintenanceRecordInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 0
    fields = ["maintenance_type", "status", "scheduled_date", "completed_date", "cost"]


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "manager"]
    search_fields = ["name", "code"]
    inlines = [AssetInline]


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "user", "department", "role", "is_active"]
    list_filter = ["department", "is_active"]
    search_fields = ["employee_id", "user__username"]


class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "department"]
    search_fields = ["name", "code"]


class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


class AssetAdmin(admin.ModelAdmin):
    list_display = ["asset_tag", "name", "category", "location", "status", "condition", "assigned_to"]
    list_filter = ["category", "location", "status", "condition"]
    search_fields = ["name", "asset_tag", "serial_number"]
    inlines = [MaintenanceRecordInline]
    readonly_fields = ["created_at", "updated_at"]


class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ["asset", "maintenance_type", "status", "scheduled_date", "completed_date", "cost"]
    list_filter = ["status", "maintenance_type", "completed_date"]
    search_fields = ["asset__name", "description"]
    readonly_fields = ["created_at", "updated_at"]


class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ["asset", "maintenance_type", "frequency", "next_maintenance_date"]
    list_filter = ["frequency"]
    search_fields = ["asset__name"]
    readonly_fields = ["created_at", "updated_at"]


class AssetAssignmentAdmin(admin.ModelAdmin):
    list_display = ["asset", "assigned_to", "department", "assigned_from", "assigned_to_date"]
    list_filter = ["department", "assigned_from"]
    search_fields = ["asset__asset_tag", "assigned_to__username"]


class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["asset", "action", "user", "timestamp"]
    list_filter = ["action", "timestamp"]
    search_fields = ["asset__asset_tag", "description"]
    readonly_fields = ["timestamp"]


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(AssetCategory, AssetCategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(MaintenanceRecord, MaintenanceRecordAdmin)
admin.site.register(MaintenanceSchedule, MaintenanceScheduleAdmin)
admin.site.register(AssetAssignment, AssetAssignmentAdmin)
admin.site.register(AuditLog, AuditLogAdmin)
