from django.urls import path

from .views import AssetCreateView, AssetDeleteView, AssetDetailView, AssetListView, AssetUpdateView, DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("assets/", AssetListView.as_view(), name="asset-list"),
    path("assets/create/", AssetCreateView.as_view(), name="asset-create"),
    path("assets/<int:pk>/", AssetDetailView.as_view(), name="asset-detail"),
    path("assets/<int:pk>/edit/", AssetUpdateView.as_view(), name="asset-update"),
    path("assets/<int:pk>/delete/", AssetDeleteView.as_view(), name="asset-delete"),
]
