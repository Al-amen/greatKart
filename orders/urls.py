from django.urls import path
from .import views
app_name = 'orders'

urlpatterns = [
    path('order_place',views.order_place,name='order_place'),
]
