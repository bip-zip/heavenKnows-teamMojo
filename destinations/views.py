from django.shortcuts import render

from django.views.generic import ListView
from django.db.models import Q
from .models import Destination, Category, Tag


class DestinationListView(ListView):
    """View to list all destinations with search and filters"""
    model = Destination
    template_name = 'destinations/destination_list.html'
    context_object_name = 'destinations'
    paginate_by = 12

    def get_queryset(self):
        queryset = Destination.objects.filter(
            is_active=True
        ).select_related('category').prefetch_related('tags', 'images')

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(full_description__icontains=search_query) |
                Q(district__icontains=search_query) |
                Q(province__icontains=search_query)
            )

        # Filter by category
        category_slug = self.request.GET.get('category', '')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filter by tags
        tag_slug = self.request.GET.get('tag', '')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        # Filter by difficulty
        difficulty = self.request.GET.get('difficulty', '')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        # Filter by district
        district = self.request.GET.get('district', '')
        if district:
            queryset = queryset.filter(district__icontains=district)

        return queryset.order_by('-is_featured', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_tag'] = self.request.GET.get('tag', '')
        context['selected_difficulty'] = self.request.GET.get('difficulty', '')
        context['selected_district'] = self.request.GET.get('district', '')
        
        # Get all categories for chips
        context['categories'] = Category.objects.all()
        
        # Get all tags
        context['tags'] = Tag.objects.all()
        
        # Get unique districts
        context['districts'] = Destination.objects.filter(
            is_active=True
        ).values_list('district', flat=True).distinct().order_by('district')
        
        # Difficulty choices
        context['difficulty_choices'] = Destination.DIFFICULTY_CHOICES
        
        return context



from django.views.generic import DetailView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
import os
import google.generativeai as genai

from .models import Destination, Itinerary
from businesses.models import BusinessProfile
from packages.models import TourPackage


class DestinationDetailView(DetailView):
    """Detailed view of a destination"""
    model = Destination
    template_name = 'destinations/destination_detail.html'
    context_object_name = 'destination'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        destination = self.get_object()
        
        # Get manual itineraries
        context['manual_itineraries'] = destination.itineraries.filter(
            source='ADMIN',
            is_default=True
        ).prefetch_related('days').first()
        
        # Get all itineraries for duration options
        context['all_itineraries'] = destination.itineraries.filter(
            source='ADMIN'
        ).values('duration_days').distinct()
        
        # Get 360 images
        context['images_360'] = destination.images.filter(is_360=True)
        context['regular_images'] = destination.images.filter(is_360=False)
        
        # Get nearby destinations (same district, different destination)
        context['nearby_destinations'] = Destination.objects.filter(
            district=destination.district,
            is_active=True
        ).exclude(id=destination.id)[:4]
        
        # Get nearby businesses (same district)
        context['nearby_businesses'] = BusinessProfile.objects.filter(
            district=destination.district,
            is_verified=True
        ).select_related('user').prefetch_related('images')[:6]
        
        # Get packages that include this destination
        context['related_packages'] = TourPackage.objects.filter(
            destinations=destination,
            status='PUBLISHED'
        ).select_related('travel_business')[:4]
        
        # Increment view count
        destination.view_count += 1
        destination.save(update_fields=['view_count'])
        
        return context

from decouple import config
import logging
# Configure logger
logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def generate_ai_itinerary(request, slug):
    """Generate AI itinerary using Google Gemini"""
    try:
        # Get destination
        destination = get_object_or_404(Destination, slug=slug, is_active=True)
        
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        days = int(data.get('days', destination.min_days or 3))
        budget_level = data.get('budget', 'moderate').lower()
        if budget_level not in ['low', 'moderate', 'high']:
            budget_level = 'moderate'

        # === Secure API Key Configuration ===
        api_key = config('GEMINI_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY not set in environment variables")
            return JsonResponse({
                'success': False,
                'error': 'Server configuration error: Missing API key'
            }, status=500)

        genai.configure(api_key=api_key)

        # === Select Model ===
        # Use gemini-1.5-flash (faster) or gemini-1.5-pro (more accurate)
        model_name = "gemini-2.5-flash"  # or "gemini-1.5-pro"

        # === Safety Settings (Recommended) ===
        safety_settings = [
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        # === Generation Config ===
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",  # Critical: Force JSON output
        }

        # === Create Prompt ===
        prompt = f"""
You are a professional travel planner for Nepal. Create a detailed {days}-day itinerary for {destination.name} in {destination.district}, Nepal.

Destination Details:
- Location: {destination.district}, {destination.province}
- Difficulty: {destination.get_difficulty_display()}
- Elevation: {destination.elevation}m
- Category: {destination.category.name}
- Description: {destination.short_description}

Budget Level: {budget_level} (low = budget, moderate = standard, high = luxury)

Return **only valid JSON** (no markdown, no ```json blocks) in this exact structure:

{{
    "total_estimated_cost": 25000,
    "cost_breakdown": {{
        "accommodation": 8000,
        "food": 5000,
        "transportation": 6000,
        "activities": 4000,
        "miscellaneous": 2000
    }},
    "daily_itinerary": [
        {{
            "day": 1,
            "title": "Arrival and Local Exploration",
            "activities": ["Arrive in Kathmandu", "Visit local market"],
            "accommodation": "Standard hotel in city center",
            "meals": "Lunch: Momos, Dinner: Dal Bhat",
            "estimated_cost": 3500,
            "tips": "Exchange currency at airport"
        }}
    ],
    "best_time_to_visit": "March-May, September-November",
    "what_to_pack": ["Warm jacket", "Trekking shoes", "Sunscreen"],
    "important_notes": ["Carry water purifier", "Respect local customs"]
}}
"""

        # === Generate Content ===
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        response = model.generate_content(prompt)

        # === Extract Response Text ===
        if not response.text:
            raise ValueError("Empty response from Gemini")

        response_text = response.text.strip()

        # Clean any accidental markdown (shouldn't happen with response_mime_type)
        if response_text.startswith("```"):
            response_text = response_text.split("```", 1)[1].rsplit("```", 1)[0].strip()

        # === Parse JSON ===
        try:
            itinerary_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}\nResponse: {response_text}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to parse AI response as JSON'
            }, status=500)

        # === Optional: Save to Database ===
        if request.user.is_authenticated:
            try:
                ai_itinerary = Itinerary.objects.create(
                    destination=destination,
                    title=f"{days}-Day AI Itinerary for {destination.name}",
                    duration_days=days,
                    source='AI',
                    created_by=request.user
                )

                for day_data in itinerary_data.get('daily_itinerary', []):
                    ItineraryDay.objects.create(
                        itinerary=ai_itinerary,
                        day_number=day_data.get('day'),
                        title=day_data.get('title', f"Day {day_data.get('day')}"),
                        description='\n'.join(day_data.get('activities', [])),
                        meals_included=day_data.get('meals', ''),
                        accommodation_type=day_data.get('accommodation', ''),
                        estimated_cost=day_data.get('estimated_cost')
                    )
            except Exception as db_error:
                logger.warning(f"Failed to save itinerary to DB: {db_error}")

        # === Return Success ===
        return JsonResponse({
            'success': True,
            'itinerary': itinerary_data
        })

    except Exception as e:
        logger.exception("Error in generate_ai_itinerary")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)