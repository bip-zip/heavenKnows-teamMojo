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