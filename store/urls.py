from django.urls import path
from store import views
app_name = 'store'
urlpatterns = [
    path('',views.StoreView.as_view(), name='store'),
   # path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.StoreView.as_view(), name='product_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
   # path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'), # funtion based view
    path('search/',views.ProductSearchView.as_view(),name='search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]
