from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product
from .models import Cart,CartItem
from django.views import View

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_to_cart(request,product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id = _cart_id(request))
    
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        cart_item.save()
    return  redirect('carts:cart')

class AddToCartView(View):
    def get_cart_id(self, request):
        cart_id = request.session.session_key
        if not cart_id:
            cart_id = request.session.create()
        return cart_id

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        cart_id = self.get_cart_id(request)

        cart, created = Cart.objects.get_or_create(cart_id=cart_id)

        cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart)
        if not created:
            cart_item.quantity += 1
        cart_item.save()

        return redirect('carts:cart')

    # def post(self, request, product_id):
    #     self.add_to_cart(request, product_id)
    #     return redirect('carts:cart')

    # def get(self, request, product_id):
    #     self.add_to_cart(request, product_id)
    #     return redirect('carts:cart')



def cart(request,total=0,quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total = (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except Cart.DoesNotExist:
        cart_items = []
        total = 0
        quantity = 0
    tax = (total * 0.2)
    grand_total = total + tax
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'carts/cart.html',context=context)
