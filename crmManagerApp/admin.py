from django.contrib import admin
from .models import Customer
# Register your models here.

class OurCustomers(admin.ModelAdmin):
    list_display = ['customer_name','customer_company','arrived_date','deal_won','deal_assigned']
    list_per_page = 5
    list_filter = ['deal_won', 'deal_assigned','customer_company']
    search_fields = ['customer_name','customer_company']

admin.site.register(Customer,OurCustomers)

admin.site.site_header = 'CRM Software'
admin.site.index_title = 'CRM Admin'