from django.contrib import admin
from .models import Customers, Loans, Payment

admin.site.register(Customers)
admin.site.register(Loans)
admin.site.register(Payment)