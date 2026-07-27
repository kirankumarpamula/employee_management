# employee/admin.py
from django.contrib import admin

from employee.models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin configuration for the Employee model."""

    list_display = ("id", "name", "salary", "age", "phone")
    search_fields = ("name",)
    list_filter = ("age",)
