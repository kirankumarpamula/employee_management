# Employee Management API

A production-quality Django REST Framework project that exposes a simple,
well-tested REST API for managing employee records.

Built with:

- Python 3.12+
- Django 5.x
- Django REST Framework
- SQLite
- Function-Based Views only (`APIView` / `@api_view` — no generic views,
  no viewsets, no routers, no JWT, no Docker, no Celery, no Redis)
- pytest + pytest-django for testing

---

## 1. Project Structure

```
employee_management/
    manage.py
    requirements.txt
    pytest.ini
    README.md
    employee_management/
        __init__.py
        settings.py
        urls.py
        wsgi.py
        asgi.py
    employee/
        __init__.py
        apps.py
        admin.py
        models.py
        serializers.py
        views.py
        urls.py
        migrations/
            __init__.py
            0001_initial.py
        tests/
            __init__.py
            test_api.py
```

---

## 2. Setup Instructions

### 2.1 Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

```bash
# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2.2 Install dependencies

```bash
pip install -r requirements.txt
```

### 2.3 Run migrations

```bash
python manage.py migrate
```

### 2.4 Create a superuser (optional, for /admin/ access)

```bash
python manage.py createsuperuser
```

### 2.5 Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/employees/`.

### 2.6 Run the test suite

```bash
pytest
```

This runs the full suite with coverage reporting enabled (see `pytest.ini`),
targeting 90%+ coverage of the `employee` app. An HTML coverage report is
generated in `htmlcov/index.html`.

---

## 3. API Endpoints

| # | Method | Endpoint                              | Description                          |
|---|--------|----------------------------------------|---------------------------------------|
| 1 | POST   | `/api/employees/`                      | Create a new employee                 |
| 2 | GET    | `/api/employees/`                      | List all employees                    |
| 3 | GET    | `/api/employees/<id>/`                 | Retrieve an employee by id            |
| 4 | PUT    | `/api/employees/<id>/`                 | Fully update an employee              |
| 5 | PATCH  | `/api/employees/<id>/`                 | Partially update an employee          |
| 6 | DELETE | `/api/employees/<id>/`                 | Delete an employee                    |
| 7 | GET    | `/api/employees/search/?name=John`     | Search employees by name (substring)  |
| 8 | GET    | `/api/employees/high-salary/`          | Employees with salary > 50000         |
| 9 | GET    | `/api/employees/age/<int:age>/`        | Employees matching an exact age       |
| 10| GET    | `/api/employees/stats/`                | Aggregate salary statistics           |

### Validation rules

| Field  | Rule                                  |
|--------|----------------------------------------|
| name   | Required, minimum 3 characters         |
| salary | Must be greater than 0                 |
| age    | Must be between 18 and 60 (inclusive)  |
| phone  | Must be exactly 10 digits              |

---

## 4. Example Requests & Responses

### 4.1 Create an employee

**Request**

```http
POST /api/employees/
Content-Type: application/json

{
    "name": "John Doe",
    "salary": 60000.00,
    "age": 30,
    "phone": "9876543210"
}
```

**Response `201 Created`**

```json
{
    "id": 1,
    "name": "John Doe",
    "salary": "60000.00",
    "age": 30,
    "phone": "9876543210"
}
```

**Validation error response `400 Bad Request`**

```json
{
    "phone": ["Phone number must be exactly 10 digits."]
}
```

### 4.2 List all employees

**Request**

```http
GET /api/employees/
```

**Response `200 OK`**

```json
[
    {
        "id": 1,
        "name": "John Doe",
        "salary": "60000.00",
        "age": 30,
        "phone": "9876543210"
    }
]
```

### 4.3 Retrieve a single employee

```http
GET /api/employees/1/
```

`200 OK` with the employee object, or `404 Not Found` if the id doesn't exist:

```json
{
    "detail": "No Employee matches the given query."
}
```

### 4.4 Update an employee (full)

```http
PUT /api/employees/1/
Content-Type: application/json

{
    "name": "John Doe",
    "salary": 65000.00,
    "age": 31,
    "phone": "9876543210"
}
```

`200 OK` with the updated object. All fields are required for `PUT`.

### 4.5 Partially update an employee

```http
PATCH /api/employees/1/
Content-Type: application/json

{
    "salary": 70000.00
}
```

`200 OK` with the updated object; only the supplied field(s) change.

### 4.6 Delete an employee

```http
DELETE /api/employees/1/
```

`204 No Content`.

### 4.7 Search employees by name

```http
GET /api/employees/search/?name=John
```

`200 OK` with a list of matching employees (case-insensitive substring match).
Returns `400 Bad Request` if the `name` query parameter is omitted.

### 4.8 High-salary employees

```http
GET /api/employees/high-salary/
```

`200 OK` with all employees whose salary is strictly greater than 50000.

### 4.9 Employees by exact age

```http
GET /api/employees/age/30/
```

`200 OK` with all employees whose age equals 30.

### 4.10 Employee statistics

```http
GET /api/employees/stats/
```

**Response `200 OK`**

```json
{
    "total_employees": 20,
    "average_salary": 56000.0,
    "maximum_salary": 98000.0,
    "minimum_salary": 22000.0
}
```

On an empty database, all numeric aggregates are returned as `0` rather
than `null` to keep the response shape consistent for clients.

---

## 5. Testing with Postman

1. Import the base URL `http://127.0.0.1:8000/api/employees/` as a Postman
   environment variable, e.g. `{{base_url}}`.
2. Create requests for each endpoint listed in the table above, matching
   method and path.
3. For `POST` / `PUT` / `PATCH`, set the request body to `raw` / `JSON` and
   use the example payloads shown in section 4.
4. Run `python manage.py runserver` first so the API is reachable.

---

## 6. Notes on Architecture

- Only `APIView` and `@api_view` are used — no `GenericAPIView` subclasses,
  no `ViewSet`s, and no DRF `Router`s, per project requirements.
- All input validation lives in `EmployeeSerializer`, keeping views thin and
  focused on HTTP concerns (status codes, request/response handling).
- `get_object_or_404` is used in `EmployeeDetailView` so that missing
  records automatically produce a `404 Not Found` with a standard DRF
  error body, without manual `try/except` boilerplate.
- Literal-path routes (`search/`, `high-salary/`, `stats/`, `age/<int:age>/`)
  are declared before the generic `<int:pk>/` route in `employee/urls.py`
  to keep URL resolution unambiguous.
