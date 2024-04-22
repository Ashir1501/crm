from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.login, name='login'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('logout', views.user_logout, name='logout'),
    path('chart/', include('chart.urls')),
]