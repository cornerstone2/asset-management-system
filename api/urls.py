from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AssetCategoryViewSet,
    AssetViewSet,
    LocationViewSet,
    MaintenanceRecordViewSet,
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
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
