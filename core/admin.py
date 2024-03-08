from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path
from crmManagerApp.models import Customer, Deal, Task, Interaction
from userManagerApp.models import Assigner
from django.contrib.auth.models import Group, User
from django.db.models import Sum
from datetime import date

# Register your models here.

class CustomLoginAdminSite(admin.AdminSite):
    login_template = 'login.html'
custom_login_admin_site = CustomLoginAdminSite(name='custom_login_admin')

@staff_member_required
def admin_statistics_view(request):
    customers = Customer.objects.filter(deal_won=True).count()
    earnings = Deal.objects.aggregate(total_amount=Sum('deal_amount'))['total_amount']
    deals = Deal.objects.all().count()
    successfullDeals = Deal.objects.filter(deal_status="Closed").count()
    tasks = Task.objects.all().count()
    completedTask = Task.objects.filter(task_status="Closed").count()
    current_date = date.today()
    upcomming_task = Task.objects.filter(task_dueDate__gt=current_date)[:3]
    customer_ids = Customer.objects.values_list('id',flat=True)
    interactions = Interaction.objects.filter(interacted_customer__id__in=customer_ids)
    if interactions.exists():
        latest_interaction = interactions.latest('interacted_time')
    else:
        latest_interaction = None
    context = {
        'customers':customers,
        'earnings':earnings,
        'deals':deals,
        'successfullDeals':successfullDeals,
        'tasks':tasks,
        'completedTask':completedTask,
        "upcomming_task":upcomming_task,
        "latest_interaction":latest_interaction,
        "title": "Statistics"
    }
    return render(request, "admin/statistics.html",context)

@login_required(login_url='login')
@staff_member_required
def admin_assigner_view(request):
    assgner = Assigner.objects.all()
    customers = Customer.objects.filter(deal_won=True).values_list('customer_name',flat=True)
    customers = list(customers) #this list has all customers who have won the deal
    #this iteration will remove customers if they are already assigned a manager
    for ass in assgner:
        if ass.customer.customer_name in customers:
            customers.remove(ass.customer.customer_name)
    manager_group = Group.objects.get(name='manager')
    manager_users = list(User.objects.filter(groups=manager_group)) #list of user objects who are managers
    manager_userslist = [user.username for user in manager_users] #list of manager users name
    if customers:
        if request.method == 'POST':
            post = Assigner()
            customerName = request.POST.get('customer')
            customerObj = Customer.objects.get(customer_name=customerName)
            post.customer = customerObj
            post.manager_name = request.POST.get('manager')
            post.save()
            return redirect('admin-assigner')
    else:            
        messages.error(request,"No customers to assign")
    context = {
        'customers':customers,
        'manager_users':manager_userslist
    }
    return render(request,'admin/assigner.html',context)

class CustomAdminSite(admin.AdminSite):
    def get_app_list(self,request,_=None):
        app_list = super().get_app_list(request)
        app_list += [
            {
                "name":"Metrics",
                "app_label":"metrics",
                "models":[
                    {
                        "name":"Statistics",
                        "object_name":"statistics",
                        "admin_url":"statistics/",
                        "view_only":True,
                    }
                ],
            },
            {
                "name":"Assign Managers",
                "app_label":"assign_managers",
                "models":[
                    {
                        "name":"Assigner",
                        "object_name":"assigner",
                        "admin_url":"assigner/",
                    }
                ],
            }
        ]
        return app_list
    
    def get_urls(self):
        urls = super().get_urls()
        urls += [
            path("statistics/",admin_statistics_view, name="admin-statistics"),
            path("assigner/",admin_assigner_view, name="admin-assigner"),
        ]
        return urls
