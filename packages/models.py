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