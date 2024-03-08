from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LogoutView
from crmManagerApp.models import Customer, Deal, Task, Interaction
from userManagerApp.models import Assigner
from django.contrib.auth.models import Group, User
from .models import Assigner
from django.db.models import Sum

# Create your views here.
class CustomLogoutView(LogoutView):
    next_page = '/'

@login_required(login_url='login')
def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
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
            }
            return render(request, 'index.html',context)
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

@login_required(login_url='login')
def assigner(request):
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
            return redirect('assigner')
    else:            
        messages.error(request,"No customers to assign")
    context = {
        'customers':customers,
        'manager_users':manager_userslist
    }
    return render(request,'assign_manager.html',context)

@login_required(login_url='login')
def user_detail(request,pk):
    users = get_object_or_404(User,pk=pk)
    user_group = users.groups.values_list('name', flat=True)[0]
    if user_group == 'normal':
        username = users.username
        registeredCustomerCount = Customer.objects.filter(custRegiteredByUser = username).count() 
        dealWonCount = Customer.objects.filter(custRegiteredByUser = username, deal_won = True).count()
        dealLostCount = Customer.objects.filter(custRegiteredByUser = username, deal_won = False).count()

        context = {
            'groups':user_group,
            'users':username,
            'registeredCustomerCount':registeredCustomerCount,
            'dealWonCount':dealWonCount,
            'dealLostCount':dealLostCount
        }
    if user_group == 'manager':
        username = users.username
        pending_deals = Assigner.objects.filter(manager_name=username,customer__deal_assigned=False).count()
        total_deals = Deal.objects.filter(dealCreatedByUser = username).count()
        lost_deals = Deal.objects.filter(dealCreatedByUser = username, deal_status= "Lost").count()
        success_deals = Deal.objects.filter(dealCreatedByUser = username, deal_status= "Closed").count()
        ongoing_deals = Deal.objects.filter(dealCreatedByUser = username, deal_status= "Open").count()
        total_earnings = Deal.objects.filter(dealCreatedByUser = username).aggregate(total_amount=Sum('deal_amount'))['total_amount']
        total_task = Task.objects.filter(taskCreatedByUser = username).count()
        completed_task = Task.objects.filter(taskCreatedByUser = username, task_status="Closed").count()

        context = {
            'groups':user_group,
            'users':username,
            'pending_deals':pending_deals,
            'total_deals': total_deals,
            'lost_deals': lost_deals,
            'success_deals': success_deals,
            'ongoing_deals': ongoing_deals,
            'total_earnings': total_earnings,
            'total_task': total_task,
            'completed_task':completed_task
        }
    return render(request,'user_detail.html',context)

@login_required(login_url='login')
def getManagerUsers(request):
    manager = Group.objects.get(name='manager')
    manager_users = User.objects.filter(groups=manager)
    context = {
        'manager_users':manager_users
    }
    return render(request,'manager_users.html',context)
@login_required(login_url='login')
def getNormalUsers(request):
    normal = Group.objects.get(name='normal')
    normal_users = User.objects.filter(groups=normal)
    context = {
        'normal_users':normal_users
    }
    return render(request,'normal_users.html',context)