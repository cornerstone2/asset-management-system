from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import AssetForm
from .models import Asset


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "assets/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_assets"] = Asset.objects.count()
        context["available_assets"] = Asset.objects.filter(status="available").count()
        context["assigned_assets"] = Asset.objects.filter(status="assigned").count()
        context["maintenance_assets"] = Asset.objects.filter(status="maintenance").count()
        context["recent_assets"] = Asset.objects.select_related("category", "location").order_by("-created_at")[:5]
        return context


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    paginate_by = 15

    def get_queryset(self):
        return Asset.objects.select_related("category", "location", "assigned_to").order_by("name")


class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["maintenance_records"] = self.object.maintenance_records.all()[:10]
        context["assignment_history"] = self.object.assignments.all()[:10]
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
