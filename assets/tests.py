{% extends 'assets/base.html' %}

{% block title %}Delete Asset{% endblock %}

{% block content %}
<div class="card">
    <h1>Delete Asset</h1>
    <p>Are you sure you want to delete <strong>{{ object.name }}</strong> ({{ object.asset_tag }})?</p>
    <form method="post">
        {% csrf_token %}
        <button class="btn danger" type="submit">Confirm Delete</button>
        <a class="btn secondary" href="{% url 'asset-detail' object.pk %}">Cancel</a>
    </form>
</div>
{% endblock %}
