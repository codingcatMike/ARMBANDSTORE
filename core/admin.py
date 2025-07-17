from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product, PurchaseRequest

admin.site.register(Product)
admin.site.register(PurchaseRequest)
