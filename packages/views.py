from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.db import transaction
import json

from .forms import TourPackageForm
from .models import TourPackage, PackageItinerary
from destinations.models import Destination


class PackageCreateView(LoginRequiredMixin, CreateView):
    """Create a new tour package"""
    model = TourPackage
    form_class = TourPackageForm
    template_name = 'packages/create.html'
    success_url = reverse_lazy('packages:list')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is a travel business
        if not request.user.is_authenticated or request.user.user_type != 'TRAVEL_BUSINESS':
            messages.error(request, 'Only travel businesses can create packages.')
            return redirect('accounts:profile')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Set the travel business
                package = form.save(commit=False)
                package.travel_business = self.request.user.business_profile
                package.save()
                form.save_m2m()  # Save many-to-many relationships (destinations)
                
                # Handle itinerary data from JavaScript
                itinerary_data = self.request.POST.get('itinerary_json')
                if itinerary_data:
                    itineraries = json.loads(itinerary_data)
                    for day_data in itineraries:
                        PackageItinerary.objects.create(
                            package=package,
                            day_number=day_data['day'],
                            title=day_data['title'],
                            description=day_data['description'],
                            destination_id=day_data.get('destination_id')
                        )
                
                messages.success(self.request, 'Package created successfully!')
                return redirect(self.success_url)
                
        except Exception as e:
            messages.error(self.request, f'Error creating package: {str(e)}')
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_destinations'] = Destination.objects.filter(is_active=True).select_related('category')
        return context
    

from django.views.generic import ListView
from django.db.models import Q, Min, Max
from .models import TourPackage


class PackageListView(ListView):
    """View to list all published tour packages with filters"""
    model = TourPackage
    template_name = 'packages/package_list.html'
    context_object_name = 'packages'
    paginate_by = 12

    def get_queryset(self):
        queryset = TourPackage.objects.filter(
            status='PUBLISHED'
        ).select_related('travel_business').prefetch_related('destinations')

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(travel_business__business_name__icontains=search_query) |
                Q(destinations__name__icontains=search_query)
            ).distinct()

        # Filter by duration
        duration_filter = self.request.GET.get('duration', '')
        if duration_filter:
            if duration_filter == '1-3':
                queryset = queryset.filter(duration_days__gte=1, duration_days__lte=3)
            elif duration_filter == '4-7':
                queryset = queryset.filter(duration_days__gte=4, duration_days__lte=7)
            elif duration_filter == '8-14':
                queryset = queryset.filter(duration_days__gte=8, duration_days__lte=14)
            elif duration_filter == '15+':
                queryset = queryset.filter(duration_days__gte=15)

        # Filter by price range
        price_filter = self.request.GET.get('price', '')
        if price_filter:
            if price_filter == 'budget':
                queryset = queryset.filter(price_per_person__lt=20000)
            elif price_filter == 'moderate':
                queryset = queryset.filter(price_per_person__gte=20000, price_per_person__lt=50000)
            elif price_filter == 'premium':
                queryset = queryset.filter(price_per_person__gte=50000, price_per_person__lt=100000)
            elif price_filter == 'luxury':
                queryset = queryset.filter(price_per_person__gte=100000)

        # Filter by destination
        destination_id = self.request.GET.get('destination', '')
        if destination_id:
            queryset = queryset.filter(destinations__id=destination_id)

        # Sort
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by == 'price_low':
            queryset = queryset.order_by('price_per_person')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price_per_person')
        elif sort_by == 'duration_short':
            queryset = queryset.order_by('duration_days')
        elif sort_by == 'duration_long':
            queryset = queryset.order_by('-duration_days')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-view_count')
        else:
            queryset = queryset.order_by('-is_featured', '-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_duration'] = self.request.GET.get('duration', '')
        context['selected_price'] = self.request.GET.get('price', '')
        context['selected_destination'] = self.request.GET.get('destination', '')
        context['selected_sort'] = self.request.GET.get('sort', '-created_at')
        
        # Get all destinations for filter
        from destinations.models import Destination
        context['all_destinations'] = Destination.objects.filter(is_active=True).order_by('name')
        
        # Get price range for display
        price_stats = TourPackage.objects.filter(status='PUBLISHED').aggregate(
            min_price=Min('price_per_person'),
            max_price=Max('price_per_person')
        )
        context['min_price'] = price_stats['min_price'] or 0
        context['max_price'] = price_stats['max_price'] or 0
        
        return context
    
from django.views.generic import DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Avg, Count
from django.db import transaction

from .models import TourPackage, PackageReview, PackageBooking
from .forms import PackageReviewForm, PackageBookingForm


class PackageDetailView(DetailView):
    """Detailed view of a tour package"""
    model = TourPackage
    template_name = 'packages/package_detail.html'
    context_object_name = 'package'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return TourPackage.objects.filter(status='PUBLISHED').select_related(
            'travel_business__user'
        ).prefetch_related('destinations', 'itinerary_days', 'reviews__user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        package = self.get_object()
        
        # Reviews and ratings
        reviews = package.reviews.all()
        context['reviews'] = reviews
        context['review_count'] = reviews.count()
        
        # Average rating
        rating_stats = reviews.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        context['avg_rating'] = rating_stats['avg_rating'] or 0
        
        # Rating distribution
        context['rating_distribution'] = {
            5: reviews.filter(rating=5).count(),
            4: reviews.filter(rating=4).count(),
            3: reviews.filter(rating=3).count(),
            2: reviews.filter(rating=2).count(),
            1: reviews.filter(rating=1).count(),
        }
        
        # Check if user has already reviewed
        if self.request.user.is_authenticated:
            context['user_has_reviewed'] = reviews.filter(user=self.request.user).exists()
            context['user_review'] = reviews.filter(user=self.request.user).first()
        else:
            context['user_has_reviewed'] = False
            context['user_review'] = None
        
        # Forms
        context['review_form'] = PackageReviewForm()
        context['booking_form'] = PackageBookingForm(initial={
            'lead_traveler_name': self.request.user.get_full_name() if self.request.user.is_authenticated else '',
            'lead_traveler_email': self.request.user.email if self.request.user.is_authenticated else '',
            'number_of_travelers': package.group_size_min
        })
        
        # Similar packages
        context['similar_packages'] = TourPackage.objects.filter(
            status='PUBLISHED',
            destinations__in=package.destinations.all()
        ).exclude(id=package.id).distinct()[:3]
        
        # Increment view count
        package.view_count += 1
        package.save(update_fields=['view_count'])
        
        return context


class PackageReviewCreateView(LoginRequiredMixin, CreateView):
    """Create a review for a package"""
    model = PackageReview
    form_class = PackageReviewForm
    
    def form_valid(self, form):
        package = get_object_or_404(TourPackage, slug=self.kwargs['slug'], status='PUBLISHED')
        
        # Check if user already reviewed
        if PackageReview.objects.filter(package=package, user=self.request.user).exists():
            messages.error(self.request, 'You have already reviewed this package.')
            return redirect('packages:detail', slug=package.slug)
        
        review = form.save(commit=False)
        review.package = package
        review.user = self.request.user
        review.save()
        
        messages.success(self.request, 'Thank you for your review!')
        return redirect('packages:detail', slug=package.slug)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors in your review.')
        return redirect('packages:detail', slug=self.kwargs['slug'])


class PackageBookingCreateView(LoginRequiredMixin, CreateView):
    """Create a booking for a package"""
    model = PackageBooking
    form_class = PackageBookingForm
    
    def form_valid(self, form):
        package = get_object_or_404(TourPackage, slug=self.kwargs['slug'], status='PUBLISHED')
        
        try:
            with transaction.atomic():
                booking = form.save(commit=False)
                booking.package = package
                booking.user = self.request.user
                
                # Calculate total amount
                booking.total_amount = package.price_per_person * booking.number_of_travelers
                
                # Validate group size
                if booking.number_of_travelers < package.group_size_min:
                    messages.error(self.request, f'Minimum group size is {package.group_size_min} travelers.')
                    return self.form_invalid(form)
                
                if booking.number_of_travelers > package.group_size_max:
                    messages.error(self.request, f'Maximum group size is {package.group_size_max} travelers.')
                    return self.form_invalid(form)
                
                booking.save()
                
                messages.success(
                    self.request, 
                    f'Booking request submitted successfully! Your booking number is {booking.booking_number}. '
                    f'The travel agency will contact you shortly.'
                )
                return redirect('packages:booking_confirmation', booking_number=booking.booking_number)
        
        except Exception as e:
            messages.error(self.request, f'Booking failed: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors in your booking form.')
        return redirect('packages:detail', slug=self.kwargs['slug'])


class BookingConfirmationView(LoginRequiredMixin, DetailView):
    """Booking confirmation page"""
    model = PackageBooking
    template_name = 'packages/booking_confirmation.html'
    context_object_name = 'booking'
    slug_field = 'booking_number'
    slug_url_kwarg = 'booking_number'
    
    def get_queryset(self):
        return PackageBooking.objects.filter(user=self.request.user).select_related('package', 'package__travel_business')