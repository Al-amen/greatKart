from django.contrib import admin

from .models import Cart, CartItem


class CartAdmin(admin.ModelAdmin):
    list_display = ("cart_id", "date_added")
    search_fields = ("cart_id",)
    list_per_page = 10


admin.site.register(Cart, CartAdmin)


class CartItemAdmin(admin.ModelAdmin):
    list_display = ("product", "cart", "quantity", "is_active")
    search_fields = ("product",)
    list_per_page = 10


admin.site.register(CartItem, CartItemAdmin)
