from django.contrib import admin
from main.models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('manufacturer','brand', 'name', 'description', 'url')

# Register your models here.
admin.site.register(Product, ProductAdmin)