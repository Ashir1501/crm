# Generated by Django 4.2.10 on 2024-02-23 10:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crmManagerApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assigner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manager_name', models.CharField(max_length=100)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmManagerApp.customer')),
            ],
        ),
    ]