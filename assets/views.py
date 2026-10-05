from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
from datetime import timedelta

from .forms import AssetForm, MaintenanceRecordForm
from .models import Asset, AuditLog, Department, MaintenanceRecord


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "assets/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_assets"] = Asset.objects.count()
        context["available_assets"] = Asset.objects.filter(status="available").count()
        context["assigned_assets"] = Asset.objects.filter(status="assigned").count()
        context["maintenance_assets"] = Asset.objects.filter(status="maintenance").count()
        context["retired_assets"] = Asset.objects.filter(status="retired").count()
        context["recent_assets"] = Asset.objects.select_related("category", "location").order_by("-created_at")[:5]
        context["departments"] = Department.objects.count()

        soon = timezone.now().date() + timedelta(days=30)
        context["warranty_expiring"] = Asset.objects.filter(warranty_end__lte=soon, warranty_end__gte=timezone.now().date()).count()
        context["overdue_maintenance"] = MaintenanceRecord.objects.filter(status="pending", scheduled_date__lt=timezone.now().date()).count()
        context["pending_maintenance"] = MaintenanceRecord.objects.filter(status="pending").count()
		context["total_asset_value"] = sum(asset.current_value() for asset in Asset.objects.all())
        return context


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    paginate_by = 20

    def get_queryset(self):
        queryset = Asset.objects.select_related("category", "location", "assigned_to").order_by("name")
        status_filter = self.request.GET.get("status")
        search = self.request.GET.get("search")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(asset_tag__icontains=search) | Q(serial_number__icontains=search))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Asset.STATUS_CHOICES
        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset = self.object
        context["maintenance_records"] = asset.maintenance_records.all()[:10]
        context["assignment_history"] = asset.assignments.all()[:10]
        context["audit_logs"] = asset.audit_logs.all()[:10]
        context["depreciation"] = f"${asset.calculate_depreciation():,.2f}"
        context["current_value"] = f"${asset.current_value():,.2f}"
        context["warranty_valid"] = asset.is_warranty_valid()
        context["maintenance_schedule"] = getattr(asset, "maintenance_schedule", None)
        return context


class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("asset-list")


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("asset-list")


class AssetDeleteView(LoginRequiredMixin, DeleteView):
    model = Asset
    template_name = "assets/asset_confirm_delete.html"
    success_url = reverse_lazy("asset-list")


class MaintenanceListView(LoginRequiredMixin, ListView):
    model = MaintenanceRecord
    template_name = "assets/maintenance_list.html"
    context_object_name = "maintenance_records"
    paginate_by = 20

    def get_queryset(self):
        queryset = MaintenanceRecord.objects.select_related("asset", "performed_by").order_by("-scheduled_date")
        status_filter = self.request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = MaintenanceRecord.STATUS_CHOICES
        context["overdue_count"] = MaintenanceRecord.objects.filter(status="pending", scheduled_date__lt=timezone.now().date()).count()
        return context


class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = "assets/maintenance_form.html"
    success_url = reverse_lazy("maintenance-list")


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = "assets/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_assets"] = Asset.objects.count()
        context["total_purchase_cost"] = Asset.objects.aggregate(Sum("purchase_cost"))["purchase_cost__sum"] or 0
        context["total_current_value"] = sum(asset.current_value() for asset in Asset.objects.all())
        context["total_depreciation"] = context["total_purchase_cost"] - context["total_current_value"]
        context["assets_by_category"] = Asset.objects.values("category__name").annotate(count=Count("id"))
        context["assets_by_status"] = Asset.objects.values("status").annotate(count=Count("id"))
        context["assets_by_location"] = Asset.objects.values("location__name").annotate(count=Count("id"))
        context["maintenance_summary"] = MaintenanceRecord.objects.values("status").annotate(count=Count("id"))
        context["recently_updated"] = Asset.objects.order_by("-updated_at")[:10]
        context["audit_logs"] = AuditLog.objects.order_by("-timestamp")[:20]
        return context
