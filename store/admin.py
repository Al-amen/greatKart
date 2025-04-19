from django.contrib import admin

from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'is_available', 'created_date', 'modified_date')
    prepopulated_fields = {'slug': ('product_name',)}
    list_editable = ('price', 'stock', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('product_name',)
    list_per_page = 10
admin.site.register(Product, ProductAdmin)