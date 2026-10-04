from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import AssetForm
from .models import Asset, AssetAttachment
from .permissions import user_can_manage_assets


class BaseAssetPermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            if not user_can_manage_assets(request.user):
                raise PermissionDenied("Only managers and technicians can manage asset records.")
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "assets/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context["total_assets"] = Asset.objects.count()
        context["available_assets"] = Asset.objects.filter(status="available").count()
        context["assigned_assets"] = Asset.objects.filter(status="assigned").count()
        context["maintenance_assets"] = Asset.objects.filter(status="maintenance").count()
        context["critical_assets"] = Asset.objects.filter(condition="critical").count()
        context["warranty_expiring"] = Asset.objects.filter(warranty_end__isnull=False, warranty_end__lte=today + timedelta(days=90)).count()
        context["maintenance_due"] = Asset.objects.filter(
            maintenance_schedule__next_maintenance_date__isnull=False,
            maintenance_schedule__next_maintenance_date__lte=today + timedelta(days=30),
        ).count()
        context["recent_assets"] = Asset.objects.select_related("category", "location").order_by("-created_at")[:5]
        context["maintenance_due_assets"] = Asset.objects.filter(
            maintenance_schedule__next_maintenance_date__isnull=False,
            maintenance_schedule__next_maintenance_date__lte=today + timedelta(days=30),
        ).select_related("category", "location").order_by("maintenance_schedule__next_maintenance_date")[:5]
        context["asset_attachments"] = AssetAttachment.objects.count()
        return context


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    paginate_by = 15

    def get_queryset(self):
        queryset = Asset.objects.select_related("category", "location", "assigned_to")
        search_term = self.request.GET.get("q")
        if search_term:
            queryset = queryset.filter(
                name__icontains=search_term
                | (
                    "asset_tag__icontains=search_term"
                )
            )
        return queryset.order_by("name")


class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["maintenance_records"] = self.object.maintenance_records.all()[:10]
        context["assignment_history"] = self.object.assignments.all()[:10]
        context["attachments"] = self.object.attachments.all()[:10]
        context["maintenance_due"] = self.object.is_maintenance_due()
        context["warranty_expiring"] = self.object.is_warranty_expiring()
        return context


class AssetCreateView(BaseAssetPermissionMixin, LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("asset-list")


class AssetUpdateView(BaseAssetPermissionMixin, LoginRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("asset-list")


class AssetDeleteView(BaseAssetPermissionMixin, LoginRequiredMixin, DeleteView):
    model = Asset
    template_name = "assets/asset_confirm_delete.html"
    success_url = reverse_lazy("asset-list")
