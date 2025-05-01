import datetime
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from sslcommerz_python_api import SSLCSession

from carts.models import CartItem
from store.models import Product

from .forms import OrderForm
from .models import Order, OrderProduct, Payment


@login_required
@csrf_exempt
def payments(request):
    mypayment = SSLCSession(
        sslc_is_sandbox=True,
        sslc_store_id=settings.SSLCOMMERZ_STORE_ID,
        sslc_store_pass=settings.SSLCOMMERZ_STORE_PASSWORD,
    )

    status_url = request.build_absolute_uri(reverse("orders:payment_status"))

    mypayment.set_urls(
        success_url=status_url,
        fail_url=status_url,
        cancel_url=status_url,
        ipn_url=status_url,  #'example.com/payment_notification'
    )

    order = Order.objects.filter(user=request.user, is_ordered=False).last()

    mypayment.set_product_integration(
        total_amount=order.order_total,
        currency="BDT",
        product_category="cloth",
        product_name="demo product",
        num_of_item=2,
        shipping_method="YES",
        product_profile="None",
    )

    mypayment.set_customer_info(
        name=order.full_name,
        email=order.email,
        address1=order.address_line_1,
        address2=order.address_line_2,
        city=order.division,
        postcode="1207",
        country=order.country,
        phone=order.phone,
    )

    mypayment.set_shipping_info(
        shipping_to=order.full_name,
        address=order.full_address,
        city=order.division,
        postcode="1209",
        country=order.country,
    )

    mypayment.set_additional_values(
        value_a=order.order_number,
        value_b=request.user.id,
    )

    response_data = mypayment.init_payment()

    # You can Print the response data
    print(response_data)

    return redirect(response_data["GatewayPageURL"])


@csrf_exempt
def payment_status(request):
    if request.method == "POST":
        request_data = request.POST
        if request_data.get("status") == "VALID":
            order_number = request_data.get("value_a")  # Get from post
            try:
                order = Order.objects.get(
                    order_number=order_number,
                    is_ordered=False,
                    user_id=request_data.get("value_b"),
                )
            except Order.DoesNotExist:
                return JsonResponse({"status": "failed", "message": "Order not found"})

            info = {
                "val_id": request_data.get("val_id"),
                "tran_id": request_data.get("tran_id"),
                "amount": request_data.get("amount"),
                "status": request_data.get("status"),
                "order_number": order_number,
                "payment_id": request_data.get("tran_id"),
            }
            query_string = urlencode(info)
            redirect_url = reverse("orders:order_complete") + f"?{query_string}"
            return redirect(redirect_url)
        else:
            return JsonResponse({"status": "failed", "message": "Payment failed"})
    else:
        return JsonResponse({"status": "failed", "message": "Invalid request method"})


def order_complete(request):
    current_user = request.user

    order_number = request.GET.get("order_number")
    transID = request.GET.get("payment_id")
    amount = request.GET.get("amount")
    status = request.GET.get("status")

    try:
        order = Order.objects.get(
            order_number=order_number, is_ordered=False, user_id=current_user
        )
        # order = Order.objects.get(order_number=order_number, is_ordered=False,user_id=request_data.get('value_b') )
        payment = Payment.objects.create(
            user=current_user,
            payment_id=transID,
            amount_paid=amount,
            payment_method="SSLCOMMERZ",
            status=status,
        )

        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = CartItem.objects.filter(user=current_user)

        for item in cart_items:
            order_product = OrderProduct()
            order_product.order = order
            order_product.payment = payment
            order_product.user = current_user
            order_product.product = item.product
            order_product.quantity = item.quantity
            order_product.product_price = item.product.price
            order_product.ordered = True
            order_product.save()

            # variations
            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variation.all()
            order_product.variations.set(product_variation)
            order_product.save()

            # Reduce stock
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # Clear cart
        CartItem.objects.filter(user=current_user).delete()

        # Send email
        mail_subject = "Thank you for your order!"
        message = render_to_string(
            "orders/order_recieved_email.html",
            {
                "user": current_user,
                "order": order,
            },
        )
        to_email = current_user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        # Display order summary
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = sum(
            [item.product_price * item.quantity for item in ordered_products]
        )

        context = {
            "order": order,
            "ordered_products": ordered_products,
            "order_number": order.order_number,
            "transID": payment.payment_id,
            "payment": payment,
            "subtotal": subtotal,
        }
        return render(request, "orders/order_complete.html", context)

    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect("home")


def order_place(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect("store:store")

    grand_total = 0
    tax = 0
    quantity = 0

    for cart_item in cart_items:
        total += cart_item.quantity * cart_item.product.price
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.phone = form.cleaned_data["phone"]
            data.email = form.cleaned_data["email"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.country = form.cleaned_data["country"]
            data.division = form.cleaned_data["division"]
            data.district = form.cleaned_data["district"]
            data.order_note = form.cleaned_data["order_note"]
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")  # Optional

            data.save()

            # Generate order number
            current_date = datetime.date.today().strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number
            )
            context = {
                "cart_items": cart_items,
                "tax": tax,
                "total": total,
                "grand_total": grand_total,
                "order": order,
                "quantity": quantity,
                "order_number": order_number,
            }

            return render(request, "orders/payments.html", context)
        else:
            return redirect("carts:checkout")
