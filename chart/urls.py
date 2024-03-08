from django.urls import path, include
from . import views

urlpatterns = [
    path("filter-options/", views.get_filter_options, name="chart-filter-options"),
    path("deals/<int:year>/", views.get_deals_chart, name="chart-deals"),
    path("average-deal/<int:year>/", views.average_deal, name="average-deal"),
    path("total-deals-status/<int:year>/", views.total_deal_status_chart, name="total-deal-status-chart"),
    path("total-task-status/<int:year>/", views.total_task_status_chart, name="total-task-status-chart"),
    path("customer-registered/<int:year>/",views.get_customersRegistered,name='customer-registered'),
    path("customer-dealwon/<int:year>/",views.get_customersDealWonStatus,name='customer-dealwon'),
    path("task-status/<int:year>/",views.taskStatus,name="taskStatus"),
    path("deal-Status/<int:year>/",views.dealStatus,name="dealStatus"),
    path("deals-with-Manager/<int:year>",views.dealMadeByManager,name="dealManager"),
    path("all-customers",views.getAllCustomers,name="allCustomers"),
    path("customersRegistered/<int:year>",views.get_deals,name="customersRegistered"),
]