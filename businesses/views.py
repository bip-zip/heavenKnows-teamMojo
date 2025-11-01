from django.shortcuts import redirect
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .forms import BusinessRegistrationForm
from .models import BusinessProfile, AccommodationDetails, ManufacturerDetails, BusinessImage
from packages.models import TourPackage, PackageReview, PackageBooking
# import Sum
from django.db.models import Sum

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


class BusinessDashboardView( TemplateView):
    """Unified business dashboard"""
    template_name = 'businesses/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_business_user:
            messages.error(request, 'Access denied. Business account required.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            business = user.business_profile
            context['business'] = business
            context['business_type'] = business.business_type
            
            # Common stats
            context['is_verified'] = business.is_verified
            
            # Travel Business Dashboard
            if user.user_type == 'TRAVEL_BUSINESS':
                packages = TourPackage.objects.filter(travel_business=business)
                context['packages'] = packages.order_by('-created_at')
                context['total_packages'] = packages.count()
                context['published_packages'] = packages.filter(status='PUBLISHED').count()
                context['draft_packages'] = packages.filter(status='DRAFT').count()
                
                # Booking stats
                bookings = PackageBooking.objects.filter(package__travel_business=business)
                context['bookings'] = bookings.select_related('user', 'package').order_by('-created_at')[:10]
                context['total_bookings'] = bookings.count()
                context['pending_bookings'] = bookings.filter(status='PENDING').count()
                context['confirmed_bookings'] = bookings.filter(status='CONFIRMED').count()
                
                # Revenue stats
                revenue_stats = bookings.filter(status__in=['CONFIRMED', 'COMPLETED']).aggregate(
                    total_revenue=Sum('total_amount')
                )
                context['total_revenue'] = revenue_stats['total_revenue'] or 0
            
            # Local Business (Hotel/Homestay/Restaurant)
            elif user.user_type == 'LOCAL_BUSINESS':
                try:
                    context['accommodation_details'] = business.accommodation_details
                except AccommodationDetails.DoesNotExist:
                    context['accommodation_details'] = None
                
                context['images'] = business.images.all()
            
            # Manufacturer
            elif user.user_type == 'MANUFACTURER':
                try:
                    context['manufacturer_details'] = business.manufacturer_details
                except ManufacturerDetails.DoesNotExist:
                    context['manufacturer_details'] = None
                
                context['images'] = business.images.all()
        
        except BusinessProfile.DoesNotExist:
            messages.error(self.request, 'Business profile not found.')
            return redirect('home')
        
        return context


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
    

from django.views.generic import UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse

from .forms import AccommodationDetailsForm, ManufacturerDetailsForm, BusinessImageForm
from .models import BusinessProfile, AccommodationDetails, ManufacturerDetails, BusinessImage


class AccommodationDetailsUpdateView(LoginRequiredMixin, UpdateView):
    """Update or create accommodation details"""
    model = AccommodationDetails
    form_class = AccommodationDetailsForm
    template_name = 'businesses/accommodation_form.html'
    success_url = reverse_lazy('accounts:business_dashboard')
    
    def get_object(self, queryset=None):
        business = self.request.user.business_profile
        obj, created = AccommodationDetails.objects.get_or_create(business=business)
        return obj
    
    def form_valid(self, form):
        messages.success(self.request, 'Accommodation details updated successfully!')
        return super().form_valid(form)


class ManufacturerDetailsUpdateView(LoginRequiredMixin, UpdateView):
    """Update or create manufacturer details"""
    model = ManufacturerDetails
    form_class = ManufacturerDetailsForm
    template_name = 'businesses/manufacturer_form.html'
    success_url = reverse_lazy('accounts:business_dashboard')
    
    def get_object(self, queryset=None):
        business = self.request.user.business_profile
        obj, created = ManufacturerDetails.objects.get_or_create(business=business)
        return obj
    
    def form_valid(self, form):
        messages.success(self.request, 'Product details updated successfully!')
        return super().form_valid(form)


class BusinessImageUploadView(LoginRequiredMixin, CreateView):
    """Upload business images"""
    model = BusinessImage
    form_class = BusinessImageForm
    template_name = 'businesses/image_upload.html'
    success_url = reverse_lazy('accounts:business_dashboard')
    
    def form_valid(self, form):
        image = form.save(commit=False)
        image.business = self.request.user.business_profile
        
        # If is_primary, unset other primary images
        if image.is_primary:
            BusinessImage.objects.filter(business=image.business, is_primary=True).update(is_primary=False)
        
        image.save()
        messages.success(self.request, 'Image uploaded successfully!')
        return super().form_valid(form)


class BusinessImageDeleteView(LoginRequiredMixin, DeleteView):
    """Delete business image"""
    model = BusinessImage
    success_url = reverse_lazy('accounts:business_dashboard')
    
    def get_queryset(self):
        return BusinessImage.objects.filter(business=self.request.user.business_profile)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Image deleted successfully!')
        return super().delete(request, *args, **kwargs)