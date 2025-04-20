from django.urls import path
from .import views
app_name = 'carts'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), # for function based view
    #path('add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'), # for class based view
    path('remove/<int:product_id>/', views.remove_cart_quantity, name='remove_cart_quantity'), # for function based view
    path('remove-cart-item<int:product_id>/', views.remove_cart_item, name='remove_cart_item'), # for function based view
    

]

