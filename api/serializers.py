from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from assets.models import Asset, AssetCategory, Location, MaintenanceRecord


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = "__all__"


class AssetSerializer(serializers.ModelSerializer):
    category = AssetCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(source="category", queryset=AssetCategory.objects.all(), write_only=True)
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(source="location", queryset=Location.objects.all(), write_only=True)

    class Meta:
        model = Asset
        fields = [
            "id",
            "name",
            "asset_tag",
            "serial_number",
            "manufacturer",
            "model",
            "category",
            "category_id",
            "location",
            "location_id",
            "status",
            "condition",
            "purchase_date",
            "purchase_cost",
            "warranty_end",
            "notes",
            "assigned_to",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "assigned_to"]


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related("category", "location", "assigned_to").all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "asset_tag", "serial_number", "manufacturer", "model"]
    ordering_fields = ["name", "created_at", "purchase_date", "status"]


class AssetCategoryViewSet(viewsets.ModelViewSet):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name"]


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name"]


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRecord.objects.select_related("asset").all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["description", "maintenance_type", "performed_by"]
    ordering_fields = ["completed_date", "created_at"]


router = DefaultRouter()
router.register(r"assets", AssetViewSet, basename="asset")
router.register(r"categories", AssetCategoryViewSet, basename="category")
router.register(r"locations", LocationViewSet, basename="location")
router.register(r"maintenance", MaintenanceRecordViewSet, basename="maintenance")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
