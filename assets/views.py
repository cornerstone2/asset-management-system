from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="managed_departments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="employees")
    role = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["employee_id"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


class AssetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "asset categories"

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="locations")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Asset(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("assigned", "Assigned"),
        ("maintenance", "Under Maintenance"),
        ("retired", "Retired"),
        ("disposed", "Disposed"),
    ]

    CONDITION_CHOICES = [
        ("new", "New"),
        ("good", "Good"),
        ("fair", "Fair"),
        ("poor", "Poor"),
        ("critical", "Critical"),
    ]

    name = models.CharField(max_length=200)
    asset_tag = models.CharField(max_length=50, unique=True)
    serial_number = models.CharField(max_length=100, blank=True)
    qr_code = models.CharField(max_length=255, blank=True, unique=True)
    manufacturer = models.CharField(max_length=120, blank=True)
    model = models.CharField(max_length=120, blank=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name="assets")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="assets")
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_assets")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default="good")
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    warranty_end = models.DateField(null=True, blank=True)
    useful_life_years = models.IntegerField(default=5, help_text="Expected lifespan in years")
    salvage_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Expected value at end of life")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["asset_tag"]),
            models.Index(fields=["status"]),
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.asset_tag})"

    def get_absolute_url(self):
        return reverse("asset-detail", kwargs={"pk": self.pk})

    def calculate_depreciation(self):
        """Calculate straight-line depreciation."""
        if not self.purchase_date or not self.purchase_cost:
            return 0

        depreciable_amount = self.purchase_cost - self.salvage_value
        annual_depreciation = depreciable_amount / self.useful_life_years

        months_owned = (timezone.now().date() - self.purchase_date).days // 30
        total_depreciation = (annual_depreciation / 12) * months_owned

        return min(total_depreciation, depreciable_amount)

    def current_value(self):
        """Calculate current book value."""
        return max(self.purchase_cost - self.calculate_depreciation(), self.salvage_value)

    def is_warranty_valid(self):
        """Check if warranty is still valid."""
        if not self.warranty_end:
            return False
        return self.warranty_end >= timezone.now().date()

    def is_maintenance_due(self, days=30):
        schedule = getattr(self, "maintenance_schedule", None)
        if not schedule or not schedule.next_maintenance_date:
            return False
        return schedule.next_maintenance_date <= timezone.now().date() + timedelta(days=days)

    def is_warranty_expiring(self, days=90):
        if not self.warranty_end:
            return False
        return self.warranty_end <= timezone.now().date() + timedelta(days=days)


class AssetAttachment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="attachments")
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="asset_attachments/%Y/%m/%d/")
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="uploaded_asset_attachments")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.name or f"Attachment for {self.asset.asset_tag}"


class MaintenanceRecord(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="maintenance_records")
    performed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="maintenance_performed")
    maintenance_type = models.CharField(max_length=120, default="Preventive")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-completed_date", "-created_at"]

    def __str__(self):
        return f"{self.asset.name} - {self.maintenance_type}"

    def is_overdue(self):
        """Check if maintenance is overdue."""
        if self.status == "completed":
            return False
        if not self.scheduled_date:
            return False
        return self.scheduled_date < timezone.now().date()


class MaintenanceSchedule(models.Model):
    FREQUENCY_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("semi_annual", "Semi-Annual"),
        ("annual", "Annual"),
    ]

    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name="maintenance_schedule")
    maintenance_type = models.CharField(max_length=120, default="Preventive")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default="monthly")
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["next_maintenance_date"]

    def __str__(self):
        return f"{self.asset.name} - {self.frequency}"

    def calculate_next_maintenance(self):
        """Calculate next maintenance date based on frequency."""
        if not self.last_maintenance_date:
            return timezone.now().date()

        frequency_days = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "quarterly": 90,
            "semi_annual": 180,
            "annual": 365,
        }
        delta = timedelta(days=frequency_days.get(self.frequency, 30))
        return self.last_maintenance_date + delta


class AssetAssignment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="assignments")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="asset_assignments")
    assigned_from = models.DateField()
    assigned_to_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="asset_assignments")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-assigned_from"]

    def __str__(self):
        return f"{self.asset.asset_tag} -> {self.assigned_to.username}"

    def is_active(self):
        """Check if assignment is currently active."""
        return self.assigned_to_date is None


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("deleted", "Deleted"),
        ("assigned", "Assigned"),
        ("maintenance", "Maintenance"),
        ("status_change", "Status Changed"),
        ("depreciation", "Depreciation Calculated"),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="audit_logs")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["asset", "-timestamp"]),
            models.Index(fields=["action", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.asset.asset_tag} - {self.action}"
