from django.shortcuts import render, redirect
from django.views.generic import ListView
from  store.models import Product
def home(request):
    return render(request, 'home.html')

class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(is_available=True)
    template_name = "home.html"
    

        
