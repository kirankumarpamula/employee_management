# employee_management/asgi.py
"""
ASGI config for the employee_management project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "employee_management.settings")

application = get_asgi_application()
