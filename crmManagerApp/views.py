from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomerRegisterForm
from django.contrib import messages
from .models import Customer, Interaction, Deal, Task
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date, time, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Create your views here.

@login_required(login_url='login')
def customerRegister(request):
    customer = Customer()
    form = CustomerRegisterForm()
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST, instance=customer)
        if form.is_valid():
            customer.deal_assigned = False
            customer.custRegiteredByUser = request.user.username
            form.save()
            messages.success(request,"Customer registered successfully")
            return redirect('dashboard')
    return render(request, 'customer_register.html', {'form_data': form})

@login_required(login_url='login')
def customerList(request):
    if request.user.is_authenticated and request.user.is_superuser:
        customers = Customer.objects.filter(deal_won = True)
        return render(request,'customer_list.html',{'customers':customers})
    user_group = request.user.groups.values_list('name', flat=True)[0]
    if user_group == 'manager':
        customerWithManager = Q(assigner__manager_name=request.user)
        dealNotassigned = Q(deal_assigned=False)
        customers = Customer.objects.filter(customerWithManager)
        customerDealNotassigned = Customer.objects.filter(customerWithManager & dealNotassigned)
        context={
            'customers':customers,
            'customerDealNotassigned': customerDealNotassigned
        }
        return render(request,'customer_list.html',context)
    customers = Customer.objects.all()
    return render(request,'customer_list.html',{'customers':customers})


@login_required(login_url='login')
def customerDetail(request, pk):
    customer_detail = Customer.objects.get(pk=pk)
    interactions = Interaction.objects.filter(interacted_customer = customer_detail.id)
    deal = Deal.objects.filter(deal_withCustomer = customer_detail.id)
    context ={
        'customer_detail': customer_detail,
        'interactions':interactions,
        'deal':deal
    }
    if interactions.exists():
        latest_interaction = interactions.latest('interacted_time').interacted_time
        latest_interaction = timezone.localtime(latest_interaction) #to localize the datetime with localtime zone
    else:
        latest_interaction = datetime.min
        latest_interaction = timezone.make_aware(latest_interaction)
        latest_interaction = timezone.localtime(latest_interaction)

    arrived_date = customer_detail.arrived_date
    arrived_date_time = datetime.combine(arrived_date, time()) # to create a naive datetime object by combining a date object with time()
    arrived_date_time = timezone.make_aware(arrived_date_time) #to make the datetime offset aware
    arrived_date_time = timezone.localtime(arrived_date_time) #to localize the date time with the localtime
    if request.user.is_superuser:
        user_group = False
    else:
        user_group = request.user.groups.values_list('name', flat=True)[0]
    if user_group == 'normal':
        if request.method == 'POST':
            if request.POST.get('interacted_mode') and request.POST.get('datetime'):
                interacted_date_time_str = request.POST.get('datetime')
                #create a datetime object and convert it to aware from naive
                interacted_date_time = timezone.make_aware(datetime.strptime(interacted_date_time_str, '%Y-%m-%dT%H:%M')) 
                interacted_date_time = timezone.localtime(interacted_date_time)
            
                if (interacted_date_time < arrived_date_time) or (interacted_date_time <= latest_interaction):
                    messages.error(request, "Interacted date and time must be greater than or equal to arrived date and previous interacted date.")
                    return render(request,'customer_detail.html',context)
                else:
                    post = Interaction()
                    post.interacted_mode = request.POST.get('interacted_mode')
                    post.interacted_time = interacted_date_time
                    post.interaction_notes = request.POST.get('notes')
                    post.interacted_customer = customer_detail
                    post.intrAddedByUser = request.user.username
                    post.save()
    if user_group == 'manager' or request.user.is_superuser:
        if request.method == 'POST':
            initiation_date_str = request.POST.get('initiationDate')
            closedate_str = request.POST.get('closeDate')

            initiation_date_obj = datetime.strptime(initiation_date_str, '%Y-%m-%d').date()
            closedate_obj = datetime.strptime(closedate_str, '%Y-%m-%d').date()

            if(initiation_date_obj < arrived_date) or (closedate_obj < initiation_date_obj+timedelta(days=6)):
                messages.error(request, "Initiation date must be >= to arrived date and close date at least should be > initiation date by 6 days.")
                return render(request,'customer_detail.html',context)
            else:
                post = Deal()
                post.deal_title = request.POST.get('title')
                post.deal_status = request.POST.get('dealstatus')
                post.deal_initiationDate = request.POST.get('initiationDate')
                post.deal_expectedCloseDate = request.POST.get('closeDate')
                post.deal_amount = request.POST.get('amount')
                post.deal_withCustomer = customer_detail
                post.dealCreatedByUser = request.user.username
                customer_detail.deal_assigned = True
                customer_detail.save()
                post.save()
                messages.success(request,"Deal created successfully")
    return render(request,'customer_detail.html',context)


@login_required(login_url='login')
@csrf_exempt
def dealAndTask(request,pk):
    deal = Deal.objects.get(pk=pk)
    tasks = Task.objects.filter(task_relatedToDeal = deal.pk)
    context={
        'deal':deal,
        'tasks':tasks
    }
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        due_date_str = request.POST.get('duedate')
        due_date_obj = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        if tasks.exists():
            latest_due_date = tasks.latest('task_dueDate').task_dueDate
        else:
            latest_due_date = date.min
        if (deal.deal_initiationDate <= due_date_obj <= deal.deal_expectedCloseDate) and (due_date_obj > latest_due_date):
            post = Task()
            post.task_title = request.POST.get('title')
            post.task_status = request.POST.get('task_status')
            post.task_description = request.POST.get('description')
            post.task_dueDate = request.POST.get('duedate')
            post.task_relatedToDeal = deal
            post.taskCreatedByUser = request.user.username
            post.save()
            return JsonResponse({'success':True})
        else:
            messages.error(request, 'Due Date must be between deal initialtion and close date and also greater than previous due date')
    return render(request,'deal_task.html',context)

@login_required(login_url='login')
def dtf(request,pk):
    deal = get_object_or_404(Deal,pk=pk)
    tasks = Task.objects.filter(task_relatedToDeal = deal.pk)
    context={
        'deal':deal,
        'tasks':tasks
    }
    return render(request,'deal_task.html',context)

@csrf_exempt
def updateDealStatus(request,pk):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        deal = get_object_or_404(Deal,pk=pk)
        deal.deal_status = request.POST.get('update_deal_status')
        deal.save()
        response_data={
            'success':True,
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error':'Bad Request'})

@csrf_exempt
def updateTaskStatus(request,pk):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        task = get_object_or_404(Task,pk=pk)
        task.task_status = request.POST.get('update_task_status')
        task.save()
        response_data={
            'success':True,
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error':'Bad Request'})


@csrf_exempt
def delete_task(request, pk):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        response_data={
            'success':True,
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error':'Bad Request'})


def delete_deal(request, pk):
    deal = Deal.objects.get(pk=pk)
    customer = Customer.objects.get(pk = deal.deal_withCustomer.pk)
    deal.delete()
    return redirect('customerDetail',customer.pk)

def delete_customer(request, pk):
    customer = Customer.objects.get(pk=pk)
    customer.delete()
    return redirect('listCustomer')

