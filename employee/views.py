# employee/views.py
"""
Function-based / APIView-based views for the Employee API.

Per project requirements, only `APIView` and `@api_view` are used.
No GenericAPIView, ViewSets, or Routers are involved anywhere in this module.
"""

from django.db.models import Avg, Max, Min
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from employee.models import Employee
from employee.serializers import EmployeeSerializer


class EmployeeListCreateView(APIView):
    """
    GET  /api/employees/       -> list all employees
    POST /api/employees/       -> create a new employee
    """

    def get(self, request):
        """Return every employee record in the database."""
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new employee record after validating the payload."""
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailView(APIView):
    """
    GET    /api/employees/<id>/   -> retrieve a single employee
    PUT    /api/employees/<id>/   -> full update
    PATCH  /api/employees/<id>/   -> partial update
    DELETE /api/employees/<id>/   -> delete
    """

    def get_object(self, pk):
        """Fetch an Employee by primary key or raise Http404."""
        return get_object_or_404(Employee, pk=pk)

    def get(self, request, pk):
        """Retrieve a single employee by id."""
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """Fully update an existing employee. All fields are required."""
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Partially update an existing employee."""
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete an employee record."""
        employee = self.get_object(pk)
        employee.delete()
        return Response(
            {"message": f"Employee with id {pk} deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET"])
def search_employees(request):
    """
    GET /api/employees/search/?name=John

    Search employees whose name contains the given (case-insensitive)
    substring. Returns 400 if the `name` query parameter is missing.
    """
    name = request.query_params.get("name")
    if not name:
        return Response(
            {"error": "Query parameter 'name' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    employees = Employee.objects.filter(name__icontains=name)
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def high_salary_employees(request):
    """
    GET /api/employees/high-salary/

    Return all employees whose salary is strictly greater than 50000.
    """
    employees = Employee.objects.filter(salary__gt=50000)
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def employees_by_age(request, age):
    """
    GET /api/employees/age/<int:age>/

    Return all employees whose age matches the given value exactly.
    """
    employees = Employee.objects.filter(age=age)
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def employee_stats(request):
    """
    GET /api/employees/stats/

    Return aggregate statistics across all employees:
        total_employees, average_salary, maximum_salary, minimum_salary.

    When the database has no employees, numeric aggregates are returned
    as 0 rather than null, to keep the response shape consistent.
    """
    aggregates = Employee.objects.aggregate(
        average_salary=Avg("salary"),
        maximum_salary=Max("salary"),
        minimum_salary=Min("salary"),
    )
    total_employees = Employee.objects.count()

    data = {
        "total_employees": total_employees,
        "average_salary": float(aggregates["average_salary"] or 0),
        "maximum_salary": float(aggregates["maximum_salary"] or 0),
        "minimum_salary": float(aggregates["minimum_salary"] or 0),
    }
    return Response(data, status=status.HTTP_200_OK)
