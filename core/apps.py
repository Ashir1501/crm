from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

class CustomAdminConfig(AdminConfig):
    default_site = "core.admin.CustomAdminSite"
