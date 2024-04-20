from django.urls import path
from . import views
urlpatterns = [
    path('register/',views.customerRegister,name='registerCustomer'),
    path('list/',views.customerList, name='listCustomer'),
    path('detail/<int:pk>/',views.customerDetail,name='customerDetail'),
    path('dealTasks/<int:pk>',views.dealAndTask,name='dealtask'),
    path('dtf/<int:pk>',views.dtf,name='dtf'),
    path('updateDeal/<int:pk>',views.updateDealStatus,name='udealstatus'),
    path('updateTask/<int:pk>',views.updateTaskStatus,name='utaskstatus'),
    path('deleteTask/<int:pk>',views.delete_task,name='delete_task'),
    path('deleteDeal/<int:pk>',views.delete_deal,name='delete_deal'),
    path('delete-customer/<int:pk>',views.delete_customer,name='delete_customer'),
]