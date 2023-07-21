# Generated by Django 4.2.3 on 2023-07-21 12:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credicts', '0006_alter_loans_contract_version_alter_loans_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loans',
            name='outstanding',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
