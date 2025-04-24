from django.shortcuts import render,redirect
from django.views import View
from django.views.generic import CreateView,TemplateView
from .forms import RegistrationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth.tokens import default_token_generator 
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import CustomUser
from django.urls import reverse_lazy

from django.contrib.auth import get_user_model
User = get_user_model()
from carts.models import Cart,CartItem
from carts.views import _cart_id
from store.models import Product


# Create your views here.
class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = form.cleaned_data['email'].split('@')[0]
        user.set_password(form.cleaned_data['password'])
        user.is_active = False
        user.save()

        current_site = get_current_site(self.request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"http://{current_site.domain}/accounts/activate/{uid}/{token}/"
        subject = "Activate your account"
        message = render_to_string('accounts/account_verification_email.html', {
            'user': user,
            'activation_link': activation_link,
        })

        to_email = user.email
        email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
        email.send()
       
       # messages.success(self.request, "An email has been sent. Please check your inbox to activate your account.")
        return redirect(f'/accounts/login/?command=verification&email={to_email}')




    
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
            return redirect('accounts:login')
        else:
            print("User is_active:", user.is_active)
            messages.error(request, "Activation link is invalid or has expired.")
            return redirect('accounts:register')

class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    print(cart_item)
                    for item in cart_item:
                        item.user = user
                        item.save()

            except:
                pass
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect('accounts:dashboard')  # Redirect to home or any other page
        else:
            messages.error(request, "Invalid credentials.")
            return render(request, self.template_name)

class CustomLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, "Logout successful.")
        return redirect('home')


class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = "accounts/dashboard.html"



class ForgotPassword(View):
    
    def get(self,request):
        return render(request,'accounts/forgot_password.html')

    def post(self,request,*args, **kwargs):
        email = request.POST.get('email')

        if CustomUser.objects.filter(email=email):
            user = CustomUser.objects.get(email__exact=email)
            current_site = get_current_site(self.request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"http://{current_site.domain}/accounts/password-reset-validate/{uid}/{token}/"
            subject = "Activate your account"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'activation_link': activation_link,
            })

            to_email = user.email
            email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
            email.send()
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('accounts:forgot-password')


class ResetPasswordValidate(View):

    def get(self,request,uidb64,token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        print(uid,user)
        
        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid'] = uid
            messages.success(request, 'Please reset your password')
            return redirect('accounts:reset-password')
        else:
            messages.error(request, 'This link has been expired!')
            return redirect('accounts:login')
            

class ResetPassword(View):
   
   def get(self,request):
       return render(request,'accounts/reset_password.html')
   

   def post(self,request):
       password = request.POST.get('password')
       confirm_password = request.POST.get('confirm_password')

       if password == confirm_password:
           uid = request.session['uid']
           user = CustomUser.objects.get(pk=uid)
           user.set_password(password)
           user.save()
           messages.success(request, 'Password reset successful')
           return redirect('accounts:login')
       else:
            messages.error(request, 'Password do not match!')
            return redirect('accounts:reset-password')
    



        


