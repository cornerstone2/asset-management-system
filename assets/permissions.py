from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AssetCategoryViewSet,
    AssetViewSet,
    LocationViewSet,
    MaintenanceRecordViewSet,
    asset_by_qr_code,
    asset_export_csv,
    asset_import_csv,
    asset_summary,
)

router = DefaultRouter()
router.register(r"assets", AssetViewSet, basename="asset")
router.register(r"categories", AssetCategoryViewSet, basename="category")
router.register(r"locations", LocationViewSet, basename="location")
router.register(r"maintenance", MaintenanceRecordViewSet, basename="maintenance")

urlpatterns = [
    path("", include(router.urls)),
    path("summary/", asset_summary, name="asset-summary"),
    path("assets/scan/<str:qr_code>/", asset_by_qr_code, name="asset-by-qr"),
    path("assets/export/csv/", asset_export_csv, name="asset-export-csv"),
    path("assets/import/csv/", asset_import_csv, name="asset-import-csv"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
