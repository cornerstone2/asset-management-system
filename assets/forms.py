from django import forms
from .models import Asset


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "name",
            "asset_tag",
            "serial_number",
            "manufacturer",
            "model",
            "category",
            "location",
            "assigned_to",
            "status",
            "condition",
            "purchase_date",
            "purchase_cost",
            "warranty_end",
            "notes",
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "warranty_end": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }
