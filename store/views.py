from django.shortcuts import render, redirect, get_object_or_404,get_list_or_404
from .models import Product, Category
from django.views.generic import ListView, DetailView
from django.db.models import Count
# Create your views here.

class StoreView(ListView):
    model = Product
    template_name = 'store/store.html'
    context_object_name = 'products'
    paginate_by = 10  # Optional: if you want pagination

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        queryset = Product.objects.filter(is_available=True).select_related('category') # N+1 fixed
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            context['total_products'] = Product.objects.filter(category=category, is_available=True).aggregate(total=Count('id'))['total']
        else:
            context['total_products'] = Product.objects.filter(is_available=True).aggregate(total=Count('id'))['total']
        
        return context

# def store(request, category_slug=None):
#     categories = None
#     products = None
#     if category_slug != None:
#         categories = get_object_or_404(Category, slug=category_slug)
#         products = Product.objects.filter(category=categories, is_available=True)
#         total_products = Product.objects.filter(category=categories,is_available=True).aggregate(total=Count('id'))['total']

#     else:
#         products = Product.objects.filter(is_available=True)
#         total_products = Product.objects.filter(is_available=True).aggregate(total=Count('id'))['total']
    
#     context = {
#         'products': products,
#         'total_products': total_products,
#     }
#     return render(request, 'store/store.html', context)


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'store/product-detail.html'

    def get_object(self, queryset=None):
        category_slug = self.kwargs.get('category_slug')
        product_slug = self.kwargs.get('product_slug')

        return get_object_or_404(
            Product,
            slug=product_slug,
            category__slug=category_slug,
            is_available=True
        )
    

def product_detail(request, category_slug, product_slug):
    # try:
    #     product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    # except Exception as e:
    #     raise e
    # context = {
    #     'product': product,
    # }
    return render(request, 'store/product-detail.html')