from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AssetAssignmentViewSet,
    AssetCategoryViewSet,
    AssetViewSet,
    AuditLogViewSet,
    DepartmentViewSet,
    EmployeeViewSet,
    LocationViewSet,
    MaintenanceRecordViewSet,
    MaintenanceScheduleViewSet,
    asset_summary,
)

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"assets", AssetViewSet, basename="asset")
router.register(r"categories", AssetCategoryViewSet, basename="category")
router.register(r"locations", LocationViewSet, basename="location")
router.register(r"maintenance", MaintenanceRecordViewSet, basename="maintenance")
router.register(r"maintenance-schedules", MaintenanceScheduleViewSet, basename="maintenance-schedule")
router.register(r"assignments", AssetAssignmentViewSet, basename="assignment")
router.register(r"audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("", include(router.urls)),
    path("summary/", asset_summary, name="asset-summary"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
