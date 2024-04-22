from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LogoutView
from crmManagerApp.models import Customer, Deal, Task, Interaction
from userManagerApp.models import Assigner
from .models import Assigner
from django.db.models import Sum

# Create your views here.
class CustomLogoutView(LogoutView):
    next_page = '/'

@login_required(login_url='login')
def dashboard(request):
    if request.user.is_authenticated:
        user_group = request.user.groups.values_list('name', flat=True)[0]
        if user_group == 'normal':
            username = request.user.username
            registeredCustomerCount = Customer.objects.filter(custRegiteredByUser = username).count() 
            dealWonCount = Customer.objects.filter(custRegiteredByUser = username, deal_won = True).count()
            dealLostCount = Customer.objects.filter(custRegiteredByUser = username, deal_won = False).count()
            customer_ids = Customer.objects.filter(custRegiteredByUser = username).values_list('id',flat=True)
            interactions = Interaction.objects.filter(interacted_customer__id__in=customer_ids) 
            if interactions.exists():
                latest_interaction = interactions.latest('interacted_time')
            else:
                latest_interaction = None
            context = {
                "registeredCustomerCount":registeredCustomerCount,
                "dealWonCount": dealWonCount,
                'dealLostCount': dealLostCount,
                'latest_interaction':latest_interaction,
            }
            return render(request, 'index_normal.html',context)
        if user_group == 'manager':
            username = request.user.username
            pending_deals = Assigner.objects.filter(manager_name=username,customer__deal_assigned=False).count()
            total_deals = Deal.objects.filter(dealCreatedByUser = username).count()
            lost_deals = Deal.objects.filter(dealCreatedByUser = username, deal_status= "Lost").count()
            success_deals = Deal.objects.filter(dealCreatedByUser = username, deal_status= "Closed").count()
            ongoing_deals = Deal.objects.filter(dealCreatedByUser = username, deal_status= "Open").count()
            total_earnings = Deal.objects.filter(dealCreatedByUser = username).aggregate(total_amount=Sum('deal_amount'))['total_amount']
            total_task = Task.objects.filter(taskCreatedByUser = username).count()
            completed_task = Task.objects.filter(taskCreatedByUser = username, task_status="Closed").count()
            current_date = date.today()
            upcomming_task = Task.objects.filter(taskCreatedByUser = username, task_dueDate__gt=current_date)[:3]
            # Filter Assigner model to get all customers assigned to the specific manager
            assigned_customers = Assigner.objects.filter(manager_name=username)
            # Extract customer IDs from the assigned customers
            customer_ids = assigned_customers.values_list('customer_id', flat=True)
            # Fetch all interactions related to the assigned customers
            interactions = Interaction.objects.filter(interacted_customer__id__in=customer_ids)
            if interactions.exists():
                latest_interaction = interactions.latest('interacted_time')
            else:
                latest_interaction = None
            context = {
                'pending_deals':pending_deals,
                'total_deals': total_deals,
                'lost_deals': lost_deals,
                'success_deals': success_deals,
                'ongoing_deals': ongoing_deals,
                'total_earnings': total_earnings,
                'total_task': total_task,
                'completed_task':completed_task,
                "upcomming_task":upcomming_task,
                "latest_interaction":latest_interaction,
            }
            return render(request, 'index_manager.html',context)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # user = User.objects.get(username = username)
        # if user.check_password(password):
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request,user)
            messages.success(request,f'Welcome {username} You have logged in Successfully.')
            if request.user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('dashboard')
        else:
            messages.error(request,"Invalid login credentials")
    return render(request,'login.html')

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    messages.success(request,f'You have logged out')
    return redirect('login')

