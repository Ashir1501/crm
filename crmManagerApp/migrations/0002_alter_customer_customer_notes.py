# Generated by Django 4.2.10 on 2024-03-04 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crmManagerApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='customer_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
