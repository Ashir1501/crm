from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.login, name='login'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('logout', views.user_logout, name='logout'),
    path('assigner/',views.assigner,name='assigner'),
    path('users/normal/',views.getNormalUsers,name='normal'),
    path('users/regular/',views.getManagerUsers,name='manager'),
    path('user/detail/<int:pk>',views.user_detail,name='user_detail'),
    path('chart/', include('chart.urls')),
]