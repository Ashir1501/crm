from django.db import models

# Create your models here.
class Customer(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=10)
    customer_company = models.CharField(max_length=100)
    customer_notes = models.TextField(null=True, blank=True)
    arrived_date = models.DateField()
    deal_won = models.BooleanField(default=False)
    deal_assigned = models.BooleanField(default=False)
    custRegiteredByUser = models.CharField(max_length=100)

    class Meta:
        db_table = 'Customer'
        ordering = ["-arrived_date"]

    def __str__(self):
        return self.customer_name
    
class Interaction(models.Model):
    interaction_option = (('Email','Email'), ('Call', 'Call'), ('Meeting','Meeting'))
    interacted_mode = models.CharField(max_length=30, choices=interaction_option)
    interacted_time = models.DateTimeField()
    interaction_notes = models.TextField(null=True)
    interacted_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    intrAddedByUser = models.CharField(max_length=100, default='')

    class Meta:
        db_table = "Interaction"
    
    def __str__(self):
        return self.interacted_mode
    
class Deal(models.Model):
    status_option = (('Lost','Lost'), ('Open','Open'), ('Closed','Closed'))
    deal_title = models.CharField(max_length=100)
    deal_status = models.CharField(max_length=30, choices=status_option)
    deal_initiationDate = models.DateField()
    deal_expectedCloseDate = models.DateField()
    deal_amount = models.IntegerField()
    deal_withCustomer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    dealCreatedByUser = models.CharField(max_length=100, default='')

    class Meta:
        db_table = 'Deal'

    def __str__(self):
        return self.deal_title
    
class Task(models.Model):
    status_option = (('Open','Open'), ('Wait','Wait'), ('Closed','Closed'))
    task_status = models.CharField(max_length=30, choices=status_option)
    task_title = models.CharField(max_length=100)
    task_description = models.TextField(null=True)
    task_dueDate = models.DateField()
    task_relatedToDeal = models.ForeignKey(Deal, on_delete=models.CASCADE)
    taskCreatedByUser = models.CharField(max_length=100, default='')

    class Meta:
        db_table = 'Task'

    def __str__(self):
        return self.task_title
