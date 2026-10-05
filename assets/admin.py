from django.contrib import admin
from .models import (
    Asset,
    AssetAssignment,
    AssetCategory,
    AuditLog,
    Department,
    Employee,
    Location,
    MaintenanceRecord,
    MaintenanceSchedule,
)


class MaintenanceInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 0
    fields = ["maintenance_type", "status", "scheduled_date", "completed_date", "cost"]


class AssetAdmin(admin.ModelAdmin):
    list_display = ["asset_tag", "name", "category", "location", "status", "condition", "assigned_to"]
    list_filter = ["category", "location", "status", "condition"]
    search_fields = ["name", "asset_tag", "serial_number", "qr_code"]
    inlines = [MaintenanceInline]
    readonly_fields = ["created_at", "updated_at"]


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "manager"]
    search_fields = ["name", "code"]


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "user", "department", "role", "is_active"]
    list_filter = ["department", "is_active"]
    search_fields = ["employee_id", "user__username"]


class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ["asset", "maintenance_type", "status", "scheduled_date", "completed_date", "cost"]
    list_filter = ["status", "maintenance_type"]
    search_fields = ["asset__name", "description"]


class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ["asset", "maintenance_type", "frequency", "next_maintenance_date"]
    list_filter = ["frequency"]


class AssetAssignmentAdmin(admin.ModelAdmin):
    list_display = ["asset", "assigned_to", "department", "assigned_from", "assigned_to_date"]
    list_filter = ["department"]


class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["asset", "action", "user", "timestamp"]
    search_fields = ["asset__asset_tag", "description"]
    readonly_fields = ["timestamp"]


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(AssetCategory)
admin.site.register(Location)
admin.site.register(Asset, AssetAdmin)
admin.site.register(MaintenanceRecord, MaintenanceRecordAdmin)
admin.site.register(MaintenanceSchedule, MaintenanceScheduleAdmin)
admin.site.register(AssetAssignment, AssetAssignmentAdmin)
admin.site.register(AuditLog, AuditLogAdmin)
