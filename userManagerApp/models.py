from django.db import models
from crmManagerApp.models import Customer
# Create your models here.
class Assigner(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    manager_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.customer}_{self.manager_name}"