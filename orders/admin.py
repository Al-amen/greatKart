from django.contrib import admin
from .models import Payment,Order,OrderProduct


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id','payment_method','amount_paid','status','created_at')
    search_fields = ('status','payment_method')



class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number','full_name','email','phone','address_line_1','order_total','tax','is_ordered', 'created_at','status')
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]

admin.site.register(Payment,PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)