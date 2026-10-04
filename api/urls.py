import csv
import io
from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from assets.models import Asset, AssetAttachment, AssetCategory, Location, MaintenanceRecord


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


class AssetAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetAttachment
        fields = ["id", "name", "description", "file", "uploaded_at", "uploaded_by"]
        read_only_fields = ["id", "uploaded_at", "uploaded_by"]


class AssetSerializer(serializers.ModelSerializer):
    category = AssetCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(source="category", queryset=AssetCategory.objects.all(), write_only=True)
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(source="location", queryset=Location.objects.all(), write_only=True)
    attachments = AssetAttachmentSerializer(many=True, read_only=True)

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
            "notes",
            "assigned_to",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "assigned_to"]


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related("category", "location", "assigned_to").all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "asset_tag", "serial_number", "manufacturer", "model", "qr_code"]
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
    today = timezone.now().date()
    total_assets = Asset.objects.count()
    available = Asset.objects.filter(status="available").count()
    assigned = Asset.objects.filter(status="assigned").count()
    maintenance = Asset.objects.filter(status="maintenance").count()
    retired = Asset.objects.filter(status="retired").count()
    disposed = Asset.objects.filter(status="disposed").count()
    maintenance_due = Asset.objects.filter(
        maintenance_schedule__next_maintenance_date__isnull=False,
        maintenance_schedule__next_maintenance_date__lte=today + timedelta(days=30),
    ).count()
    warranty_expiring = Asset.objects.filter(
        warranty_end__isnull=False,
        warranty_end__lte=today + timedelta(days=90),
    ).count()

    payload = {
        "total_assets": total_assets,
        "available_assets": available,
        "assigned_assets": assigned,
        "maintenance_assets": maintenance,
        "retired_assets": retired,
        "disposed_assets": disposed,
        "maintenance_due_soon": maintenance_due,
        "warranty_expiring_soon": warranty_expiring,
        "asset_health": {
            "healthy": available + assigned,
            "under_watch": maintenance,
            "retired": retired,
            "disposed": disposed,
        },
    }
    return Response(payload, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def asset_by_qr_code(request, qr_code):
    asset = Asset.objects.select_related("category", "location", "assigned_to").filter(qr_code=qr_code).first()
    if not asset:
        return Response({"detail": "Asset not found for the provided QR code."}, status=status.HTTP_404_NOT_FOUND)
    serializer = AssetSerializer(asset)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def asset_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="assets_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "asset_tag",
        "name",
        "category",
        "location",
        "status",
        "condition",
        "manufacturer",
        "model",
        "serial_number",
        "purchase_date",
        "purchase_cost",
        "warranty_end",
        "qr_code",
    ])

    for asset in Asset.objects.select_related("category", "location").order_by("name"):
        writer.writerow([
            asset.asset_tag,
            asset.name,
            asset.category.name if asset.category else "",
            asset.location.name if asset.location else "",
            asset.status,
            asset.condition,
            asset.manufacturer,
            asset.model,
            asset.serial_number,
            asset.purchase_date,
            asset.purchase_cost,
            asset.warranty_end,
            asset.qr_code,
        ])

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def asset_import_csv(request):
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return Response({"detail": "A CSV file is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        text = uploaded_file.read().decode("utf-8-sig")
    except Exception:
        return Response({"detail": "Could not read the uploaded CSV file."}, status=status.HTTP_400_BAD_REQUEST)

    reader = csv.DictReader(io.StringIO(text))
    created = 0
    updated = 0

    for row in reader:
        if not row.get("asset_tag"):
            continue

        category_name = (row.get("category") or "General").strip()
        location_name = (row.get("location") or "Unassigned").strip()
        category, _ = AssetCategory.objects.get_or_create(name=category_name)
        location, _ = Location.objects.get_or_create(name=location_name, defaults={"code": location_name[:10].upper()})

        defaults = {
            "name": row.get("name") or row["asset_tag"],
            "category": category,
            "location": location,
            "serial_number": row.get("serial_number") or "",
            "manufacturer": row.get("manufacturer") or "",
            "model": row.get("model") or "",
            "status": row.get("status") or "available",
            "condition": row.get("condition") or "good",
            "purchase_date": row.get("purchase_date") or None,
            "purchase_cost": row.get("purchase_cost") or 0,
            "warranty_end": row.get("warranty_end") or None,
            "qr_code": row.get("qr_code") or "",
        }

        asset, was_created = Asset.objects.update_or_create(
            asset_tag=row["asset_tag"],
            defaults=defaults,
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return Response({"created": created, "updated": updated}, status=status.HTTP_200_OK)
