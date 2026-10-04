from django import forms
from .models import Asset, MaintenanceRecord, MaintenanceSchedule, Department, Employee


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "name",
            "asset_tag",
            "serial_number",
            "qr_code",
            "manufacturer",
            "model",
            "category",
            "location",
            "assigned_to",
            "status",
            "condition",
            "purchase_date",
            "purchase_cost",
            "warranty_end",
            "useful_life_years",
            "salvage_value",
            "notes",
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "warranty_end": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }


class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            "asset",
            "performed_by",
            "maintenance_type",
            "status",
            "scheduled_date",
            "completed_date",
            "description",
            "cost",
            "notes",
        ]
        widgets = {
            "scheduled_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "completed_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }


class MaintenanceScheduleForm(forms.ModelForm):
    class Meta:
        model = MaintenanceSchedule
        fields = ["asset", "maintenance_type", "frequency", "last_maintenance_date"]
        widgets = {
            "last_maintenance_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "code", "description", "manager"]


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["user", "employee_id", "department", "role", "hire_date", "is_active"]
        widgets = {
            "hire_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }
