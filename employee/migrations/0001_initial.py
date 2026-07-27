# employee/migrations/0001_initial.py
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100,
                        validators=[django.core.validators.MinLengthValidator(3)],
                    ),
                ),
                ("salary", models.DecimalField(decimal_places=2, max_digits=12)),
                ("age", models.PositiveSmallIntegerField()),
                ("phone", models.CharField(max_length=10)),
            ],
            options={
                "ordering": ["id"],
            },
        ),
    ]
