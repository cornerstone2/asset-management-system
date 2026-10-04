{% extends 'assets/base.html' %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<div class="card">
    <h1>Operations Dashboard</h1>
    <div class="grid" style="margin-top: 1.5rem;">
        <div class="metric">
            <strong>Total Assets</strong>
            <p>{{ total_assets }}</p>
        </div>
        <div class="metric success">
            <strong>Available</strong>
            <p>{{ available_assets }}</p>
        </div>
        <div class="metric">
            <strong>Assigned</strong>
            <p>{{ assigned_assets }}</p>
        </div>
        <div class="metric warning">
            <strong>Maintenance</strong>
            <p>{{ maintenance_assets }}</p>
        </div>
        <div class="metric danger">
            <strong>Due Soon</strong>
            <p>{{ maintenance_due }}</p>
        </div>
        <div class="metric warning">
            <strong>Warranty Expiring</strong>
            <p>{{ warranty_expiring }}</p>
        </div>
        <div class="metric danger">
            <strong>Critical Assets</strong>
            <p>{{ critical_assets }}</p>
        </div>
        <div class="metric success">
            <strong>Attachments</strong>
            <p>{{ asset_attachments }}</p>
        </div>
    </div>
</div>

{% if maintenance_due_assets %}
<div class="card">
    <h2>Maintenance Due Soon</h2>
    <table>
        <thead>
            <tr>
                <th>Asset</th>
                <th>Tag</th>
                <th>Category</th>
                <th>Location</th>
                <th>Due Date</th>
            </tr>
        </thead>
        <tbody>
            {% for asset in maintenance_due_assets %}
            <tr>
                <td><a href="{% url 'asset-detail' asset.pk %}">{{ asset.name }}</a></td>
                <td>{{ asset.asset_tag }}</td>
                <td>{{ asset.category }}</td>
                <td>{{ asset.location }}</td>
                <td>{{ asset.maintenance_schedule.next_maintenance_date }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endif %}

<div class="card" style="margin-top: 2rem;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;">
        <h2>Recently Added Assets</h2>
        <a class="btn" href="{% url 'asset-create' %}">Add Asset</a>
    </div>
    <table>
        <thead>
            <tr>
                <th>Asset</th>
                <th>Tag</th>
                <th>Category</th>
                <th>Location</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for asset in recent_assets %}
            <tr>
                <td><a href="{% url 'asset-detail' asset.pk %}">{{ asset.name }}</a></td>
                <td>{{ asset.asset_tag }}</td>
                <td>{{ asset.category }}</td>
                <td>{{ asset.location }}</td>
                <td><span class="status-chip">{{ asset.get_status_display }}</span></td>
            </tr>
            {% empty %}
            <tr><td colspan="5">No assets found.</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
