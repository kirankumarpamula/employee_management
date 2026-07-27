# employee/models.py
"""
Database models for the employee app.

Only a single model, Employee, is required by the project specification.
"""

from django.core.validators import MinLengthValidator
from django.db import models


class Employee(models.Model):
    """Represents a single employee record.

    Fields:
        name: Full name of the employee. Must be at least 3 characters long.
        salary: Monthly/annual salary of the employee. Must be positive.
        age: Age of the employee. Business rules restrict this to 18-60,
             enforced at the serializer layer (kept here only as a sane
             database-level floor via PositiveSmallIntegerField).
        phone: 10-digit contact number, stored as a string to preserve
               leading zeros and avoid integer overflow / formatting issues.
    """

    name = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    age = models.PositiveSmallIntegerField()
    phone = models.CharField(max_length=10)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.id})"
