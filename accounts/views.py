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

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Registration successful! Please log in.')   
        return super().form_valid(form)
    


from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Avg, Sum

from businesses.models import BusinessProfile, AccommodationDetails, ManufacturerDetails
from packages.models import TourPackage, PackageBooking
from destinations.models import Destination


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile page for tourists"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user bookings
        context['bookings'] = PackageBooking.objects.filter(
            user=user
        ).select_related('package', 'package__travel_business').order_by('-created_at')[:10]
        
        # Get user reviews
        from packages.models import PackageReview
        context['reviews'] = PackageReview.objects.filter(
            user=user
        ).select_related('package').order_by('-created_at')[:10]
        
        # Booking stats
        booking_stats = PackageBooking.objects.filter(user=user).aggregate(
            total_bookings=Count('id'),
            total_spent=Sum('total_amount')
        )
        context['total_bookings'] = booking_stats['total_bookings'] or 0
        context['total_spent'] = booking_stats['total_spent'] or 0
        
        return context

class LogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)   # clears the session
        return redirect('accounts:login')  # use your homepage URL name here
    
