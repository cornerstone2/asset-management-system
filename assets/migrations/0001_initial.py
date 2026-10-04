from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'asset categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('asset_tag', models.CharField(max_length=50, unique=True)),
                ('serial_number', models.CharField(blank=True, max_length=100)),
                ('manufacturer', models.CharField(blank=True, max_length=120)),
                ('model', models.CharField(blank=True, max_length=120)),
                ('status', models.CharField(choices=[('available', 'Available'), ('assigned', 'Assigned'), ('maintenance', 'Under Maintenance'), ('retired', 'Retired'), ('disposed', 'Disposed')], default='available', max_length=20)),
                ('condition', models.CharField(choices=[('new', 'New'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')], default='good', max_length=20)),
                ('purchase_date', models.DateField(blank=True, null=True)),
                ('purchase_cost', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('warranty_end', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_assets', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assets', to='assets.assetcategory')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assets', to='assets.location')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='AssetAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_from', models.DateField()),
                ('assigned_to_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='assets.asset')),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_assignments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-assigned_from'],
            },
        ),
        migrations.CreateModel(
            name='MaintenanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('performed_by', models.CharField(blank=True, max_length=120)),
                ('maintenance_type', models.CharField(default='Preventive', max_length=120)),
                ('scheduled_date', models.DateField(blank=True, null=True)),
                ('completed_date', models.DateField(blank=True, null=True)),
                ('description', models.TextField()),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maintenance_records', to='assets.asset')),
            ],
            options={
                'ordering': ['-completed_date', '-created_at'],
            },
        ),
    ]
