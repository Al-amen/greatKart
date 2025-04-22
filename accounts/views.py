from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView
from .forms import RegistrationForm
from django.contrib import messages

# Create your views here.

class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = ''  # Redirect after registration

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = form.cleaned_data.get('email').split('@')[0]
        user.set_password(form.cleaned_data.get('password'))  # Important for hashing
        user.save()
        messages.success(self.request, "Registration successful.")
        return super().form_valid(form)
   