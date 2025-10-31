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


from django.views.generic import ListView
from django.db.models import Q
from .models import BusinessProfile


class LocalToGlobalView(ListView):

    model = BusinessProfile
    template_name = 'businesses/localtoglobal.html'
    context_object_name = 'businesses'
    paginate_by = 12

    def get_queryset(self):
        queryset = BusinessProfile.objects.filter(
            is_verified=True,
            business_type='MANUFACTURER'
        ).select_related('user').prefetch_related('images', 'manufacturer_details')

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(business_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(district__icontains=search_query) |
                Q(province__icontains=search_query) |
                Q(manufacturer_details__product_category__icontains=search_query) |
                Q(manufacturer_details__product_description__icontains=search_query)
            )

        # Filter by location
        district = self.request.GET.get('district', '')
        if district:
            queryset = queryset.filter(district__icontains=district)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_district'] = self.request.GET.get('district', '')
        
        # Get unique districts for filter dropdown
        context['districts'] = BusinessProfile.objects.filter(
            is_verified=True,
            business_type='MANUFACTURER'
        ).values_list('district', flat=True).distinct().order_by('district')
        
        return context