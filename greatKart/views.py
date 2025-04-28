from django.shortcuts import render, redirect
from django.views.generic import ListView
from  store.models import Product,ReviewRating
def home(request):
    return render(request, 'home.html')

class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(is_available=True).order_by('-created_date')
    template_name = "home.html"

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        products = self.get_queryset()
        reviews = None
        for product in products:
          reviews = ReviewRating.objects.filter(product_id=self.product.id, status=True)
        context[" reviews"] =  reviews
        return context
    
    

        
