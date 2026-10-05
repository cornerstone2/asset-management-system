from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from assets.models import Asset, AssetAssignment, AssetCategory, AuditLog, Department, Employee, Location, MaintenanceRecord, MaintenanceSchedule


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


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


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSchedule
        fields = "__all__"


class AssetAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetAssignment
        fields = "__all__"


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"


class AssetSerializer(serializers.ModelSerializer):
    category = AssetCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(source="category", queryset=AssetCategory.objects.all(), write_only=True)
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(source="location", queryset=Location.objects.all(), write_only=True)
    depreciation = serializers.SerializerMethodField()
    current_value = serializers.SerializerMethodField()
    warranty_valid = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            "id",
            "name",
            "asset_tag",
            "serial_number",
            "qr_code",
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
            "useful_life_years",
            "salvage_value",
            "depreciation",
            "current_value",
            "warranty_valid",
            "notes",
            "assigned_to",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "assigned_to", "depreciation", "current_value", "warranty_valid"]

    def get_depreciation(self, obj):
        return float(obj.calculate_depreciation())

    def get_current_value(self, obj):
        return float(obj.current_value())

    def get_warranty_valid(self, obj):
        return obj.is_warranty_valid()


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name"]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["employee_id", "user__username"]
    ordering_fields = ["employee_id"]


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
    search_fields = ["description", "maintenance_type", "performed_by__username"]
    ordering_fields = ["completed_date", "created_at"]

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        overdue = self.queryset.filter(status="pending", scheduled_date__lt=timezone.now().date())
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)


class MaintenanceScheduleViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSchedule.objects.all()
    serializer_class = MaintenanceScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["asset__name", "maintenance_type"]
    ordering_fields = ["next_maintenance_date"]


class AssetAssignmentViewSet(viewsets.ModelViewSet):
    queryset = AssetAssignment.objects.all()
    serializer_class = AssetAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["asset__asset_tag", "assigned_to__username"]
    ordering_fields = ["assigned_from"]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["asset__asset_tag", "action"]
    ordering_fields = ["timestamp"]


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related("category", "location", "assigned_to").all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "asset_tag", "serial_number", "manufacturer", "model", "qr_code"]
    ordering_fields = ["name", "created_at", "purchase_date", "status"]

    @action(detail=False, methods=["get"])
    def by_status(self, request):
        status_filter = request.query_params.get("status")
        assets = self.queryset.filter(status=status_filter) if status_filter else self.queryset
        return Response(self.get_serializer(assets, many=True).data)

    @action(detail=False, methods=["get"])
    def low_warranty(self, request):
        soon = timezone.now().date() + timedelta(days=30)
        assets = self.queryset.filter(warranty_end__lte=soon, warranty_end__gte=timezone.now().date())
        return Response(self.get_serializer(assets, many=True).data)

    @action(detail=False, methods=["get"])
    def by_qr(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"error": "QR code required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            asset = self.queryset.get(qr_code=code)
            return Response(self.get_serializer(asset).data)
        except Asset.DoesNotExist:
            return Response({"error": "Asset not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def asset_summary(request):
    total_assets = Asset.objects.count()
    available = Asset.objects.filter(status="available").count()
    assigned = Asset.objects.filter(status="assigned").count()
    maintenance = Asset.objects.filter(status="maintenance").count()
    retired = Asset.objects.filter(status="retired").count()
    disposed = Asset.objects.filter(status="disposed").count()

    soon = timezone.now().date() + timedelta(days=30)
    low_warranty = Asset.objects.filter(warranty_end__lte=soon, warranty_end__gte=timezone.now().date()).count()
    overdue_maintenance = MaintenanceRecord.objects.filter(status="pending", scheduled_date__lt=timezone.now().date()).count()
    total_current_value = sum(asset.current_value() for asset in Asset.objects.all())
    total_purchase_cost = Asset.objects.aggregate(Sum("purchase_cost"))["purchase_cost__sum"] or 0

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
        "maintenance_alerts": {
            "overdue_count": overdue_maintenance,
            "warranty_expiring_soon": low_warranty,
        },
        "financial": {
            "total_current_value": float(total_current_value),
            "total_purchase_cost": float(total_purchase_cost),
        },
    }
    return Response(payload, status=status.HTTP_200_OK)
