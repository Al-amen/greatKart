from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,Variation
from .models import Cart,CartItem
from django.views import View

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_to_cart(request,product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST.get(key)

            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except Variation.DoesNotExist:
                variation = None
            
 
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id = _cart_id(request))
    
    cart.save()
    print(product_variation)

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()



    # Check if the product already exists in the cart
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        # existing_variations -> database
        # current_variation -> product_variation
        # item_id -> database
        
        for item in cart_item:
            existing_variation = list(item.variation.all())
            existing_variation_sorted = sorted(existing_variation, key=lambda x: x.id)
            product_variation_sorted = sorted(product_variation, key=lambda x: x.id)

            if existing_variation_sorted == product_variation_sorted:
                item.quantity += 1
                item.save()
                break 
         
            else:
                # No matching variation, create new cart item
                new_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if product_variation:
                    new_item.variation.set(product_variation)
                new_item.save()
        
    else:
        # No item exists at all, create new
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if product_variation:
            cart_item.variation.set(product_variation)
        cart_item.save()

    return redirect('carts:cart')


def remove_cart_quantity(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('carts:cart')

def remove_cart_item(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('carts:cart')

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
            total += (cart_item.product.price * cart_item.quantity)
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
