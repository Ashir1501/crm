"""
URL configuration for crm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from userManagerApp.views import CustomLogoutView
from django.conf.urls.static import static
from django.conf import settings
from core.admin import admin_statistics_view, admin_assigner_view


urlpatterns = [
    path("admin/statistics/",admin.site.admin_view(admin_statistics_view),name="admin-statistics"),
    path("admin/assigner/",admin.site.admin_view(admin_assigner_view),name="admin-assigner"),
    path('admin/logout/', CustomLogoutView.as_view()),
    path('admin/', admin.site.urls),
    path('', include('userManagerApp.urls')),
    path('customer/', include('crmManagerApp.urls')),
]