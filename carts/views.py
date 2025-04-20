from django.shortcuts import render

def cart(request):
    return render(request, 'carts/cart.html')
