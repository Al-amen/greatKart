from django.shortcuts import render, redirect, get_object_or_404,get_list_or_404
from .models import Product, Category,ReviewRating,ProductGallery
from django.views.generic import ListView, DetailView
from django.db.models import Count
from carts.models import Cart, CartItem
from carts.views import _cart_id
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
# Create your views here.

class StoreView(ListView):
    model = Product
    template_name = 'store/store.html'
    context_object_name = 'products'
    paginate_by = 2  # Optional: if you want pagination
    page_kwarg = 'page'

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        queryset = Product.objects.filter(is_available=True).select_related('category').order_by('-created_date') # N+1 fixed
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




class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'store/product-detail.html'  # Use your old template name

    def get_object(self, queryset=None):
        category_slug = self.kwargs.get('category_slug')
        product_slug = self.kwargs.get('product_slug')
        return get_object_or_404(
            Product,
            slug=product_slug,
            category__slug=category_slug,
            is_available=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Check if product is already in the cart
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(self.request),
            product=product
        ).exists()
        context['in_cart'] = in_cart

        # Check if user has ordered this product
        orderproduct = None
        if self.request.user.is_authenticated:
            orderproduct = OrderProduct.objects.filter(
                user=self.request.user,
                product_id=product.id
            ).exists()
        context['orderproduct'] = orderproduct

        # Get reviews
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
        context['reviews'] = reviews

        #Get product gallery
        product_gallery = ProductGallery.objects.filter(product_id=product.id)
        context['product_gallery'] = product_gallery

        return context
    

def product_detail(request, category_slug, product_slug):
    # try:
    #     product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    # except Exception as e:
    #     raise e
    # context = {
    #     'product': product,
    # }
    return render(request, 'store/product-detail.html')


def search(request):
    product = None
    total_products = 0
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        product = Product.objects.filter(Q(product_name__icontains=keyword) | Q(description__icontains=keyword))
        total_products = product.count()
    else:
        product = Product.objects.all()
        total_products = product.count()
    context = {
        'products': product,
        'total_products': total_products,
    }
    return render(request, 'store/store.html', context)


class ProductSearchView(ListView):
    model = Product
    template_name = 'store/store.html'
    context_object_name = 'products'

    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            keyword = self.request.GET.get('keyword', '')
            if keyword:
                self._queryset = Product.objects.filter(
                    Q(product_name__icontains=keyword) | Q(description__icontains=keyword)
                )
            else:
                self._queryset = Product.objects.all()
        return self._queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = self.get_queryset().count()
        return context
    


def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form = ReviewForm(request.POST,instance=review)
            form.save()
            messages.success(request,'Thank you! Your review has been updated')
            return redirect(url)

        except ReviewRating.DoesNotExist:
            
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                data.status = True
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            else:
                messages.error(request, 'Invalid form submission.')
                return redirect(url)




            
            


        