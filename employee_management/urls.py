# employee_management/urls.py
"""
Root URL configuration for the employee_management project.

All employee-related API endpoints are delegated to the `employee` app,
mounted under the `/api/employees/` prefix.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/employees/", include("employee.urls")),
]
