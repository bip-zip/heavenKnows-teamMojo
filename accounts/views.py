from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView

from django.contrib.auth import logout
from django.views.generic import View

from .forms import EmailAuthenticationForm
from django.contrib import messages
from django.urls import reverse

class LoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm  

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user

        print(user, user.is_authenticated, getattr(user, 'user_type', None))  # debugging

        if getattr(user, 'user_type', None) == 'ADMIN':
            return redirect(reverse('admin:index'))

        elif user.user_type == 'TRAVEL_BUSINESS' or user.user_type == 'LOCAL_BUSINESS' or user.user_type == 'MANUFACTURER': 
            if getattr(user.business_profile, 'is_verified', False):
                return redirect('/business/dashboard')
            else:
                messages.error(self.request, 'Please wait for admin verification, you will receive a call shortly.')
                return redirect('/')
        else:
            return redirect('accounts:profile')


   


from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from .models import CustomUser

class UserRegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')  # redirect after successful registration


class ProfileView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/profile.html')

class LogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)   # clears the session
        return redirect('accounts:login')  # use your homepage URL name here
    
