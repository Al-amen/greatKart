from django.shortcuts import render, redirect
from django.views.generic import ListView
from  store.models import Product,ReviewRating



class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(is_available=True).order_by('-created_date')
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_queryset()
        product_reviews = {}  # Dictionary to store reviews for each product

        for product in products:
            # Store reviews for each product
            reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
            product_reviews[product.id] = reviews
        
        context["reviews"] = product_reviews
        return context
    

        
def home(request):
    products = Product.objects.all().filter(is_available=True)

    # Get the reviews
    # reviews = None
    # for product in products:
    #     reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
       # 'reviews': reviews,
    }
    return render(request, 'home.html', context)
