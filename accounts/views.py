import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from orders.models import Order

from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import CustomUser, UserProfile

User = get_user_model()
from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import OrderProduct


# Create your views here.
class RegisterView(CreateView):
    template_name = "accounts/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = form.cleaned_data["email"].split("@")[0]
        user.set_password(form.cleaned_data["password"])
        user.is_active = False
        user.save()

        current_site = get_current_site(self.request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = (
            f"http://{current_site.domain}/accounts/activate/{uid}/{token}/"
        )
        subject = "Activate your account"
        message = render_to_string(
            "accounts/account_verification_email.html",
            {
                "user": user,
                "activation_link": activation_link,
            },
        )

        to_email = user.email
        email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
        email.send()

        # messages.success(self.request, "An email has been sent. Please check your inbox to activate your account.")
        return redirect(f"/accounts/login/?command=verification&email={to_email}")


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            print("User is_active:", user.is_active)
            messages.success(request, "Your account has been activated successfully.")
            return redirect("accounts:login")
        else:
            print("User is_active:", user.is_active)
            messages.error(request, "Activation link is invalid or has expired.")
            return redirect("accounts:register")


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            old_cart_id = _cart_id(request)
            login(request, user)

            try:
                cart = Cart.objects.get(cart_id=old_cart_id)
                guest_cart_items = CartItem.objects.filter(cart=cart, user=None)

                for guest_item in guest_cart_items:
                    guest_variations = list(guest_item.variation.all())

                    # Check if user already has this product + variation
                    existing_items = CartItem.objects.filter(
                        user=user, product=guest_item.product
                    )
                    found_match = False

                    for existing_item in existing_items:
                        existing_variations = list(existing_item.variation.all())

                        if sorted(guest_variations, key=lambda x: x.id) == sorted(
                            existing_variations, key=lambda x: x.id
                        ):
                            # Merge: Increase quantity
                            existing_item.quantity += guest_item.quantity
                            existing_item.save()
                            found_match = True
                            break

                    if not found_match:
                        # Assign guest item to user
                        guest_item.user = user
                        guest_item.save()

            except Cart.DoesNotExist:
                print("No guest cart found")

            messages.success(request, "Login successful.")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split("=") for x in query.split("&"))
                if "next" in params:
                    nextPage = params["next"]
                    return redirect(nextPage)
            except:
                return redirect("accounts:dashboard")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("accounts:login")


class CustomLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, "Logout successful.")
        return redirect("home")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Order.objects.filter(
            user_id=self.request.user.id, is_ordered=True
        ).order_by("-created_at")
        context["orders"] = orders
        context["orders_count"] = orders.count()
        context["userprofile"] = get_object_or_404(
            UserProfile, user_id=self.request.user.id
        )
        return context


class MyOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "accounts/my_order.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(
            user_id=self.request.user.id, is_ordered=True
        ).order_by("-created_at")


class EditProfileView(LoginRequiredMixin, View):
    template_name = "accounts/edit_profile.html"

    def get(self, request):
        userprofile = get_object_or_404(UserProfile, user=request.user)
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
        context = {
            "user_form": user_form,
            "profile_form": profile_form,
            "userprofile": userprofile,
        }
        print(f"userprofile {userprofile.profile_picture.url}")
        return render(request, self.template_name, context)

    def post(self, request):
        userprofile = get_object_or_404(UserProfile, user=request.user)

        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Please correct the error below.")
            context = {
                "user_form": user_form,
                "profile_form": profile_form,
                "userprofile": userprofile,
            }
            return render(request, self.template_name, context)


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = "accounts/change_password.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = CustomUser.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(confirm_password)
                user.save()
                messages.success(request, "Password updated successfully.")
                return redirect("accounts:change-password")
            else:
                messages.error(request, "Please enter valid current password")
                return redirect("accounts:change-password")
        else:
            messages.error(request, "Password does not match!")
            return redirect("accounts:change-password")


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "accounts/order_detail.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"

    def get_object(self):
        order_number = self.kwargs.get("order_number")
        return get_object_or_404(Order, order_number=order_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        order_detail = OrderProduct.objects.filter(order=order)
        subtotal = 0
        for item in order_detail:
            subtotal += item.product_price * item.quantity
        context["order_detail"] = order_detail
        context["subtotal"] = subtotal
        return context


class ForgotPassword(View):

    def get(self, request):
        return render(request, "accounts/forgot_password.html")

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")

        if CustomUser.objects.filter(email=email):
            user = CustomUser.objects.get(email__exact=email)
            current_site = get_current_site(self.request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"http://{current_site.domain}/accounts/password-reset-validate/{uid}/{token}/"
            subject = "Activate your account"
            message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "user": user,
                    "activation_link": activation_link,
                },
            )

            to_email = user.email
            email = EmailMessage(
                subject, message, settings.DEFAULT_FROM_EMAIL, [to_email]
            )
            email.send()
            messages.success(
                request, "Password reset email has been sent to your email address."
            )
            return redirect("accounts:login")
        else:
            messages.error(request, "Account does not exist!")
            return redirect("accounts:forgot-password")


class ResetPasswordValidate(View):

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        print(uid, user)

        if user is not None and default_token_generator.check_token(user, token):
            request.session["uid"] = uid
            messages.success(request, "Please reset your password")
            return redirect("accounts:reset-password")
        else:
            messages.error(request, "This link has been expired!")
            return redirect("accounts:login")


class ResetPassword(View):

    def get(self, request):
        return render(request, "accounts/reset_password.html")

    def post(self, request):
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password == confirm_password:
            uid = request.session["uid"]
            user = CustomUser.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("accounts:login")
        else:
            messages.error(request, "Password do not match!")
            return redirect("accounts:reset-password")
