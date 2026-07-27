# employee/apps.py
from django.apps import AppConfig


class EmployeeConfig(AppConfig):
    """Configuration for the employee application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "employee"
