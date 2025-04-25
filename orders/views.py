from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import OrderForm
from .models import Payment,Order,OrderProduct
from carts.models import CartItem
import datetime

def payments(request):

    return render(request,'orders/payments.html')

def order_place(request,total=0,quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if(cart_count<=0):
        return redirect('store:store')
    
    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += cart_item.quantity*cart_item.product.price
        quantity += cart_item.quantity
    tax = (2*total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.division = form.cleaned_data['division']
            data.district = form.cleaned_data['district']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')  # Optional

            data.save()

            # Generate order number
            current_date = datetime.date.today().strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context = {
                'cart_items':cart_items,
                'tax':tax,
                'total':total,
                'grand_total':grand_total,
                'order':order

            }

            return render(request, 'orders/payments.html', context) 
        else:
            return redirect('carts:checkout') 
            

   

