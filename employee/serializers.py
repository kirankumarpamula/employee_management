# employee/serializers.py
"""
Serializers for the Employee model.

Validation rules (per project spec):
    name    - required, minimum length 3
    salary  - must be greater than 0
    age     - between 18 and 60 (inclusive)
    phone   - exactly 10 digits
"""

from rest_framework import serializers

from employee.models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for creating, reading, and updating Employee records."""

    class Meta:
        model = Employee
        fields = ["id", "name", "salary", "age", "phone"]

    def validate_name(self, value):
        """Ensure the name is present and at least 3 characters long."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required.")
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        return value.strip()

    def validate_salary(self, value):
        """Ensure salary is strictly greater than zero."""
        if value <= 0:
            raise serializers.ValidationError("Salary must be greater than 0.")
        return value

    def validate_age(self, value):
        """Ensure age falls within the allowed working-age range."""
        if value < 18 or value > 60:
            raise serializers.ValidationError("Age must be between 18 and 60.")
        return value

    def validate_phone(self, value):
        """Ensure phone number is exactly 10 numeric digits."""
        if not str(value).isdigit() or len(str(value)) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value
