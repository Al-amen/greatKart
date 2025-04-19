from django.urls import path
from store import views
app_name = 'store'
urlpatterns = [
    path('',views.StoreView.as_view(), name='store'),
   # path('', views.store, name='store'),
    path('<slug:category_slug>/', views.StoreView.as_view(), name='product_by_category'),
]
