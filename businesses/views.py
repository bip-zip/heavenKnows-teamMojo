from django.shortcuts import redirect
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import BusinessRegistrationForm
from .models import BusinessProfile

User = get_user_model()


class BusinessRegisterView(CreateView):    
    model = BusinessProfile
    form_class = BusinessRegistrationForm
    template_name = 'businesses/register.html'
    success_url = reverse_lazy('businesses:dashboard')
    
    def form_valid(self, form):
        """Handle valid form submission"""
        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    contact=form.cleaned_data['contact'],
                    user_type=self.get_user_type_from_business_type(form.cleaned_data['business_type'])
                )
                
                # Create business profile
                business_profile = form.save(commit=False)
                business_profile.user = user
                business_profile.save()
                
                
                
                messages.success(
                    self.request, 
                    'Registration successful! Your account is pending admin verification. '
                    'Please complete your business details to get started.'
                )
                
                return redirect(self.success_url)
                
        except Exception as e:
            messages.error(self.request, f'Registration failed: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle invalid form submission"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_user_type_from_business_type(self, business_type):
        """Helper method to map business type to user type"""
        if business_type == 'TRAVEL_AGENCY':
            return 'TRAVEL_BUSINESS'
        elif business_type in ['HOTEL', 'HOMESTAY', 'RESTAURANT']:
            return 'LOCAL_BUSINESS'
        elif business_type == 'MANUFACTURER':
            return 'MANUFACTURER'
        return 'TOURIST'
    
    def get_context_data(self, **kwargs):
        """Add extra context to template"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Business Registration'
        return context


class BusinessDashboardView(CreateView):
    model = BusinessProfile
    form_class = BusinessRegistrationForm
    template_name = 'businesses/dashboard.html'
    success_url = reverse_lazy('businesses:dashboard')