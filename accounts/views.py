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
        print("User ID:", user.pk)
        print("Encoded UID:", uid)
        print("Token Generated:", token)

        messages.success(self.request, "An email has been sent. Please check your inbox to activate your account.")
        return redirect(f'/accounts/login/?command=verification&email={to_email}')




    
class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        print("URL Token:", token)
        print("Is token valid?", default_token_generator.check_token(user, token))
        print("User is_active:", user.is_active)

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


class DashboardView(TemplateView):
    template_name = "accounts/dashboard.html"
