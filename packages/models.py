from django.db import models
from destinations.models import Destination
from businesses.models import BusinessProfile

# import slugify
from django.utils.text import slugify


class TourPackage(models.Model):
    """
    Tour packages created by travel businesses.
    Can include multiple destinations.
    """
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
    ]
    
    # Creator
    travel_business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='packages')
    
    # Basic info
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    
    # Destinations included
    destinations = models.ManyToManyField(Destination, related_name='packages')
    
    # Package details
    duration_days = models.PositiveIntegerField()
    duration_nights = models.PositiveIntegerField()
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, help_text="In NPR")
    group_size_min = models.PositiveIntegerField(default=1)
    group_size_max = models.PositiveIntegerField()
    
    # What's included/excluded
    inclusions = models.TextField(help_text="What's included in the package")
    exclusions = models.TextField(help_text="What's not included")
    
    # Dates
    available_from = models.DateField(null=True, blank=True)
    available_to = models.DateField(null=True, blank=True)
    
    # Media
    cover_image = models.ImageField(upload_to='packages/')
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.travel_business.business_name}"


class PackageItinerary(models.Model):
    """
    Custom itinerary for packages (different from destination itineraries).
    """
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='itinerary_days')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['package', 'day_number']
        unique_together = ['package', 'day_number']
        verbose_name_plural = "Package Itineraries"

    def __str__(self):
        return f"{self.package.title} - Day {self.day_number}"
    


from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class PackageReview(models.Model):
    """Reviews for tour packages"""
    package = models.ForeignKey('TourPackage', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='package_reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Would recommend?
    would_recommend = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['package', 'user']  # One review per user per package
    
    def __str__(self):
        return f"{self.user.email} - {self.package.title} ({self.rating}★)"


class PackageBooking(models.Model):
    """Booking requests for tour packages"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partial Payment'),
        ('PAID', 'Full Payment'),
        ('REFUNDED', 'Refunded'),
    ]
    
    # Booking reference
    booking_number = models.CharField(max_length=20, unique=True, editable=False)
    
    # Relations
    package = models.ForeignKey('TourPackage', on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='package_bookings')
    
    # Traveler details
    lead_traveler_name = models.CharField(max_length=255)
    lead_traveler_email = models.EmailField()
    lead_traveler_phone = models.CharField(max_length=15)
    number_of_travelers = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    # Trip details
    preferred_start_date = models.DateField()
    special_requests = models.TextField(blank=True)
    
    # Pricing
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='UNPAID')
    
    # Admin notes
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.booking_number:
            # Generate booking number: PKG-YYYYMMDD-XXXX
            from django.utils import timezone
            import random
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            self.booking_number = f"PKG-{date_str}-{random_str}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.booking_number} - {self.package.title}"


# Update TourPackage model to include average rating method
# Add this method to your existing TourPackage model:
"""
def get_average_rating(self):
    from django.db.models import Avg
    result = self.reviews.aggregate(Avg('rating'))
    return result['rating__avg'] or 0

def get_review_count(self):
    return self.reviews.count()
"""