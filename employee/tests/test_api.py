# employee/tests/test_api.py
"""
Comprehensive API test suite for the Employee Management API.

Covers, for every endpoint: happy paths, validation errors, 404s, and
empty-database edge cases. Uses pytest + pytest-django + DRF's APIClient.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from employee.models import Employee

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client():
    """Return a fresh DRF APIClient for each test."""
    return APIClient()


@pytest.fixture
def valid_payload():
    """A known-good employee payload."""
    return {"name": "John Doe", "salary": "60000.00", "age": 30, "phone": "9876543210"}


@pytest.fixture
def employee(db):
    """Create and return a single persisted Employee record."""
    return Employee.objects.create(name="Alice Johnson", salary=55000, age=28, phone="9123456780")


@pytest.fixture
def multiple_employees(db):
    """Create a small, varied set of Employee records for list/filter tests."""
    return [
        Employee.objects.create(name="John Smith", salary=40000, age=25, phone="9000000001"),
        Employee.objects.create(name="John Carter", salary=60000, age=30, phone="9000000002"),
        Employee.objects.create(name="Bob Marley", salary=80000, age=40, phone="9000000003"),
    ]


# ---------------------------------------------------------------------------
# 1 & 2. POST /api/employees/  and  GET /api/employees/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEmployeeListCreate:
    def test_create_employee_success(self, api_client, valid_payload):
        response = api_client.post("/api/employees/", valid_payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "John Doe"
        assert Employee.objects.count() == 1

    def test_create_employee_invalid_payload_missing_fields(self, api_client):
        response = api_client.post("/api/employees/", {"name": "John"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "salary" in response.data
        assert "age" in response.data
        assert "phone" in response.data

    def test_create_employee_name_too_short(self, api_client, valid_payload):
        valid_payload["name"] = "Al"
        response = api_client.post("/api/employees/", valid_payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_create_employee_salary_not_positive(self, api_client, valid_payload):
        valid_payload["salary"] = "0"
        response = api_client.post("/api/employees/", valid_payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "salary" in response.data

    def test_create_employee_negative_salary(self, api_client, valid_payload):
        valid_payload["salary"] = "-500"
        response = api_client.post("/api/employees/", valid_payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "salary" in response.data

    def test_create_employee_age_below_range(self, api_client, valid_payload):
        valid_payload["age"] = 17
        response = api_client.post("/api/employees/", valid_payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "age" in response.data

    def test_create_employee_age_above_range(self, api_client, valid_payload):
        valid_payload["age"] = 61
        response = api_client.post("/api/employees/", valid_payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "age" in response.data

    def test_create_employee_phone_not_10_digits(self, api_client, valid_payload):
        valid_payload["phone"] = "12345"
        response = api_client.post("/api/employees/", valid_payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone" in response.data

    def test_create_employee_phone_non_numeric(self, api_client, valid_payload):
        valid_payload["phone"] = "98ABCD1234"
        response = api_client.post("/api/employees/", valid_payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone" in response.data

    def test_get_all_employees(self, api_client, multiple_employees):
        response = api_client.get("/api/employees/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_get_all_employees_empty_database(self, api_client, db):
        response = api_client.get("/api/employees/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


# ---------------------------------------------------------------------------
# 3, 4, 5, 6. GET / PUT / PATCH / DELETE /api/employees/<id>/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEmployeeDetail:
    def test_retrieve_employee_success(self, api_client, employee):
        response = api_client.get(f"/api/employees/{employee.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Alice Johnson"

    def test_retrieve_employee_not_found(self, api_client, db):
        response = api_client.get("/api/employees/9999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_employee_full_success(self, api_client, employee):
        payload = {"name": "Alice Updated", "salary": "70000.00", "age": 29, "phone": "9123456789"}
        response = api_client.put(f"/api/employees/{employee.id}/", payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        employee.refresh_from_db()
        assert employee.name == "Alice Updated"
        assert float(employee.salary) == 70000.00

    def test_update_employee_full_missing_field_fails(self, api_client, employee):
        # PUT requires all fields; omitting one should fail validation.
        payload = {"name": "Alice Updated", "salary": "70000.00", "age": 29}
        response = api_client.put(f"/api/employees/{employee.id}/", payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone" in response.data

    def test_update_employee_not_found(self, api_client, valid_payload, db):
        response = api_client.put("/api/employees/9999/", valid_payload, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_partial_update_employee_success(self, api_client, employee):
        response = api_client.patch(
            f"/api/employees/{employee.id}/", {"salary": "99999.99"}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        employee.refresh_from_db()
        assert float(employee.salary) == 99999.99
        # Untouched fields remain unchanged.
        assert employee.name == "Alice Johnson"

    def test_partial_update_employee_invalid_value(self, api_client, employee):
        response = api_client.patch(f"/api/employees/{employee.id}/", {"age": 5}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "age" in response.data

    def test_partial_update_employee_not_found(self, api_client, db):
        response = api_client.patch("/api/employees/9999/", {"age": 40}, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_employee_success(self, api_client, employee):
        response = api_client.delete(f"/api/employees/{employee.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Employee.objects.filter(id=employee.id).exists()

    def test_delete_employee_not_found(self, api_client, db):
        response = api_client.delete("/api/employees/9999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# 7. GET /api/employees/search/?name=John
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEmployeeSearch:
    def test_search_matches_multiple(self, api_client, multiple_employees):
        response = api_client.get("/api/employees/search/", {"name": "John"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_case_insensitive(self, api_client, multiple_employees):
        response = api_client.get("/api/employees/search/", {"name": "john"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_no_matches(self, api_client, multiple_employees):
        response = api_client.get("/api/employees/search/", {"name": "Zorro"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_search_missing_query_param(self, api_client, multiple_employees):
        response = api_client.get("/api/employees/search/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_empty_database(self, api_client, db):
        response = api_client.get("/api/employees/search/", {"name": "John"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


# ---------------------------------------------------------------------------
# 8. GET /api/employees/high-salary/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestHighSalaryEmployees:
    def test_high_salary_filters_correctly(self, api_client, multiple_employees):
        response = api_client.get("/api/employees/high-salary/")
        assert response.status_code == status.HTTP_200_OK
        names = [emp["name"] for emp in response.data]
        assert "Bob Marley" in names
        assert "John Carter" in names
        assert "John Smith" not in names  # salary 40000, not > 50000

    def test_high_salary_empty_database(self, api_client, db):
        response = api_client.get("/api/employees/high-salary/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_high_salary_none_qualify(self, api_client, db):
        Employee.objects.create(name="Low Earner", salary=10000, age=22, phone="9111111111")
        response = api_client.get("/api/employees/high-salary/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


# ---------------------------------------------------------------------------
# 9. GET /api/employees/age/<int:age>/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEmployeesByAge:
    def test_age_filter_matches(self, api_client, multiple_employees):
        response = api_client.get("/api/employees/age/30/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "John Carter"

    def test_age_filter_no_matches(self, api_client, multiple_employees):
        response = api_client.get("/api/employees/age/99/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_age_filter_empty_database(self, api_client, db):
        response = api_client.get("/api/employees/age/30/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


# ---------------------------------------------------------------------------
# 10. GET /api/employees/stats/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEmployeeStats:
    def test_stats_with_data(self, api_client, multiple_employees):
        response = api_client.get("/api/employees/stats/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_employees"] == 3
        assert response.data["maximum_salary"] == 80000.0
        assert response.data["minimum_salary"] == 40000.0
        assert response.data["average_salary"] == pytest.approx(60000.0)

    def test_stats_empty_database(self, api_client, db):
        response = api_client.get("/api/employees/stats/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_employees"] == 0
        assert response.data["average_salary"] == 0
        assert response.data["maximum_salary"] == 0
        assert response.data["minimum_salary"] == 0

    def test_stats_single_employee(self, api_client, employee):
        response = api_client.get("/api/employees/stats/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_employees"] == 1
        assert response.data["average_salary"] == 55000.0
        assert response.data["maximum_salary"] == 55000.0
        assert response.data["minimum_salary"] == 55000.0
