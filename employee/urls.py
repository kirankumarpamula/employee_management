# employee/urls.py
"""
URL routing for the employee app.

NOTE: literal paths such as `search/`, `high-salary/`, `stats/`, and
`age/<int:age>/` are declared BEFORE the generic `<int:pk>/` pattern.
This ordering matters because Django resolves URLs top-to-bottom, and
without it a request like /api/employees/stats/ could otherwise be
mistakenly captured by a numeric pk pattern in some routing configurations.
"""

from django.urls import path

from employee import views

urlpatterns = [
    # Specific / literal routes first.
    path("search/", views.search_employees, name="employee-search"),
    path("high-salary/", views.high_salary_employees, name="employee-high-salary"),
    path("age/<int:age>/", views.employees_by_age, name="employee-by-age"),
    path("stats/", views.employee_stats, name="employee-stats"),
    # Collection route: list + create.
    path("", views.EmployeeListCreateView.as_view(), name="employee-list-create"),
    # Detail route: retrieve, update, partial update, delete.
    path("<int:pk>/", views.EmployeeDetailView.as_view(), name="employee-detail"),
]
