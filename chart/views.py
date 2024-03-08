from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from crmManagerApp.models import Customer, Interaction, Deal, Task
from django.db.models import F, Sum, Avg, Count
from django.db.models.functions import ExtractYear, ExtractMonth
from utils.charts import months,colorPalette, colorPrimary, colorSuccess, colorDanger, generate_color_palette, get_year_dict, generate_color_palette_border, borderColor
# Create your views here.
# for charts

# fetches all the deals, groups them by year, extracts the year from the deal_initiationDate field, and returns them in a list.
def get_filter_options(request):
    grouped_deals = Deal.objects.annotate(year=ExtractYear("deal_initiationDate")).values("year").order_by("-year").distinct()
    options = [deal["year"] for deal in grouped_deals]

    return JsonResponse({
        "options": options,
    })


# fetches all the deals (in a specific year) and their amounts, groups them by month, and calculates the monthly sum of amount.
def get_deals_chart(request, year):

    deals = Deal.objects.filter(deal_initiationDate__year=year)
    grouped_deals = deals.annotate(price=F("deal_amount")).annotate(month=ExtractMonth("deal_initiationDate"))\
        .values("month").annotate(average=Sum("deal_amount")).values("month", "average").order_by("month")

    sales_dict = get_year_dict()

    for group in grouped_deals:
        sales_dict[months[group["month"]-1]] = round(group["average"], 2)


    return JsonResponse({
        "title": f"Deal Amount in {year}",
        "data": {
            "labels": list(sales_dict.keys()),
            "datasets": [{
                "label": "Amount (\u20B9)",
                "backgroundColor": generate_color_palette(12),
                "borderColor": generate_color_palette_border(12),
                "data": list(sales_dict.values()),
                "borderWidth": 1
            }]
        },
    })


# fetches all the deals (in a specific year) and their prices, groups them by month, and calculates the average monthly price.
def average_deal(request, year):
    deals = Deal.objects.filter(deal_initiationDate__year=year)
    grouped_deals = deals.annotate(price=F("deal_amount")).annotate(month=ExtractMonth("deal_initiationDate"))\
        .values("month").annotate(average=Avg("deal_amount")).values("month", "average").order_by("month")

    spend_per_customer_dict = get_year_dict()

    for group in grouped_deals:
        spend_per_customer_dict[months[group["month"]-1]] = round(group["average"], 2)

    return JsonResponse({
        "title": f"Average Deal Amount per Month in {year}",
        "data": {
            "labels": list(spend_per_customer_dict.keys()),
            "datasets": [{
                "label": "Amount (\u20B9)",
                "backgroundColor": generate_color_palette(12),
                "borderColor": generate_color_palette_border(12),
                "data": list(spend_per_customer_dict.values()),
                "borderWidth": 1
            }]
        },
    })

# counts successful and unsuccessful deals in a specific year.
def total_deal_status_chart(request, year):
    deals = Deal.objects.filter(deal_withCustomer__deal_assigned = True, deal_expectedCloseDate__year=year)

    return JsonResponse({
        "title": f"Deal status in {year}",
        "data": {
            "labels": ["Lost", "Open","Closed"],
            "datasets": [{
                "label": "Amount (\u20B9)",
                "backgroundColor": [colorDanger,colorPrimary, colorSuccess],
                "borderColor": [colorDanger,colorPrimary, colorSuccess],
                "data": [
                    deals.filter(deal_status="Lost").count(),
                    deals.filter(deal_status="Open").count(),
                    deals.filter(deal_status="Closed").count(),
                ],
            }]
        },
    })

def total_task_status_chart(request, year):
    task = Task.objects.filter(task_relatedToDeal__deal_expectedCloseDate__year=year)

    return JsonResponse({
        "title": f"Task status in {year}",
        "data": {
            "labels": ["Open", "Wait","Closed"],
            "datasets": [{
                "backgroundColor": generate_color_palette(3),
                "borderColor": generate_color_palette(3),
                "data": [
                    task.filter(task_status="Open").count(),
                    task.filter(task_status="Wait").count(),
                    task.filter(task_status="Closed").count(),
                ],
            }]
        },
    })


def get_deals(request,year):
    deals = Deal.objects.filter(deal_initiationDate__year=year)
    group_deals = deals.annotate(month=ExtractMonth('deal_initiationDate')).values("month")\
    .annotate(count=Count('id')).order_by('month')

    deals_dict = get_year_dict()

    for group in group_deals:
        deals_dict[months[group["month"]-1]] = group["count"]

    return JsonResponse({
        "title": f"Deals Initiated in {year}",
        "data": {
            "labels": list(deals_dict.keys()),
            "datasets": [{
                "label": "Deals",
                "backgroundColor": generate_color_palette(12),
                "borderColor": generate_color_palette_border(12),
                "data": list(deals_dict.values()),
                "borderWidth": 1
            }]
        },
    })

     

def get_customersRegistered(request,year):
    
    customers = Customer.objects.filter(custRegiteredByUser = request.user.username, arrived_date__year=year)
    grouped_customerByMonth = customers.annotate(month=ExtractMonth('arrived_date')).values("month")\
        .annotate(count=Count('id')).order_by('month')
        
    sales_dict = get_year_dict()

    for group in grouped_customerByMonth:
        sales_dict[months[group["month"]-1]] = group["count"]

    return JsonResponse({
        "title": f"Customers Registered in {year}",
        "data": {
            "labels": list(sales_dict.keys()),
            "datasets": [{
                "label": "Customers",
                "backgroundColor": generate_color_palette(12),
                "borderColor": generate_color_palette_border(12),
                "data": list(sales_dict.values()),
                "borderWidth": 1
            }]
        },
    })

def getAllCustomers(request):
    customers = Customer.objects.filter(deal_won=True)
    years = customers.annotate(year=ExtractYear("arrived_date")).values("year").order_by("-year").distinct()
    years = [year["year"] for year in years]
    data = []
    for year in range(0,len(years)-1):
        customers = Customer.objects.filter(arrived_date__year=years[year])
        grouped_customerByMonth = customers.annotate(month=ExtractMonth('arrived_date')).values("month").annotate(count=Count("id")).order_by('month')

        customer_dict = get_year_dict()
        for group in grouped_customerByMonth:
            customer_dict[months[group["month"]-1]] = group["count"]
        data.append(customer_dict)
        
    datasets = []
    for year in range(0,len(years)-1):
        dataset = dict()
        dataset["label"] = f"Customers in {years[year]}"
        dataset["data"] = list(data[year].values())
        dataset["fill"] = True
        dataset["backgroundColor"] = colorPalette[year]
        dataset["borderColor"] = borderColor[year]
        dataset["pointBackgroundColor"] = borderColor[year]
        dataset["pointBorderColor"] = "#fff"
        dataset["pointHoverBackgroundColor"] = "#fff"
        dataset["pointHoverBorderColor"] = borderColor[year]
        datasets.append(dataset)


    return JsonResponse({
        "title": f"Customers Registered since {years[len(years)-2]}",
        "data": {
            "labels": list(data[0].keys()),
            "datasets":datasets,
        },
    })




def dealMadeByManager(request,year):

    deals = Deal.objects.filter(dealCreatedByUser=request.user.username, deal_initiationDate__year=year)
    grouped_deals = deals.annotate(price=F("deal_amount")).annotate(month=ExtractMonth("deal_initiationDate"))\
        .values("month").annotate(total=Sum("deal_amount")).values("month", "total").order_by("month")

    sales_dict = get_year_dict()

    for group in grouped_deals:
        sales_dict[months[group["month"]-1]] = round(group["total"], 2)


    return JsonResponse({
        "title": f"Deals amount generated in {year}",
        "data": {
            "labels": list(sales_dict.keys()),
            "datasets": [{
                "label": "Amount (\u20B9)",
                "backgroundColor": generate_color_palette(12),
                "borderColor": generate_color_palette_border(12),
                "data": list(sales_dict.values()),
                "borderWidth": 1
            }]
        },
    })

def get_customersDealWonStatus(request, year):
    
    customers = Customer.objects.filter(custRegiteredByUser = request.user.username, arrived_date__year=year)

    return JsonResponse({
        "title": f"Deal won status in {year}",
        "data": {
            "labels": ["Won", "Lost"],
            "datasets": [{
                "backgroundColor": [colorSuccess, colorDanger],
                "borderColor": [colorSuccess, colorDanger],
                "data": [
                    customers.filter(deal_won=True).count(),
                    customers.filter(deal_won=False).count(),
                ],
            }]
        },
    })

def taskStatus(request, year):
    task = Task.objects.filter(taskCreatedByUser=request.user.username, task_relatedToDeal__deal_expectedCloseDate__year=year)

    return JsonResponse({
        "title": f"Task status in {year}",
        "data": {
            "labels": ["Open", "Wait","Closed"],
            "datasets": [{
                "backgroundColor": generate_color_palette(3),
                "borderColor": generate_color_palette(3),
                "data": [
                    task.filter(task_status="Open").count(),
                    task.filter(task_status="Wait").count(),
                    task.filter(task_status="Closed").count(),
                ],
            }]
        },
    })

def dealStatus(request, year):
    deal = Deal.objects.filter(dealCreatedByUser=request.user.username, deal_expectedCloseDate__year=year)

    return JsonResponse({
        "title": f"Deal status in {year}",
        "data": {
            "labels": ["Closed", "Open","Lost"],
            "datasets": [{
                "backgroundColor": [colorPalette[1],colorPalette[2],colorPalette[3]],
                "borderColor": [colorPalette[1],colorPalette[2],colorPalette[3]],
                "data": [
                    deal.filter(deal_status="Closed").count(),
                    deal.filter(deal_status="Open").count(),
                    deal.filter(deal_status="Lost").count(),
                ],
            }]
        },
    })