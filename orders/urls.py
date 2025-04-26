from django.urls import path
from .import views
app_name = 'orders'

urlpatterns = [
    path('order_place',views.order_place,name='order_place'),
    path('payments/',views.payments,name='payments'),
    path('payments/sslc/status',views.payment_status,name='payment_status'),
    path('payments/sslc/order_complete/',views.order_complete,name='order_complete'),
]
