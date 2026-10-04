from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "asset_tag", "serial_number", "manufacturer", "model"]
    ordering_fields = ["name", "created_at", "purchase_date", "status"]


class AssetCategoryViewSet(viewsets.ModelViewSet):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name"]


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name"]


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRecord.objects.select_related("asset").all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["description", "maintenance_type", "performed_by"]
    ordering_fields = ["completed_date", "created_at"]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def asset_summary(request):
    total_assets = Asset.objects.count()
    available = Asset.objects.filter(status="available").count()
    assigned = Asset.objects.filter(status="assigned").count()
    maintenance = Asset.objects.filter(status="maintenance").count()
    retired = Asset.objects.filter(status="retired").count()
    disposed = Asset.objects.filter(status="disposed").count()

    payload = {
        "total_assets": total_assets,
        "available_assets": available,
        "assigned_assets": assigned,
        "maintenance_assets": maintenance,
        "retired_assets": retired,
        "disposed_assets": disposed,
        "asset_health": {
            "healthy": available + assigned,
            "under_watch": maintenance,
            "retired": retired,
            "disposed": disposed,
        },
    }
    return Response(payload, status=status.HTTP_200_OK)
