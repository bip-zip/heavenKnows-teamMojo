from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """
    Main categories for destinations (trek, adventure, mountain climb, religious, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For icon class names
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Tags for destinations (adventure, climbing, trekking, culture, etc.)
    More flexible than categories - destinations can have multiple tags.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Destination(models.Model):
    """
    Main destination model with all details.
    """
    
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MODERATE', 'Moderate'),
        ('HARD', 'Hard'),
        ('EXTREME', 'Extreme'),
    ]
    
    # Basic info
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='destinations')
    tags = models.ManyToManyField(Tag, related_name='destinations', blank=True)
    
    # Description
    short_description = models.TextField(max_length=500)
    full_description = models.TextField()
    
    # Location
    district = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    elevation = models.PositiveIntegerField(null=True, blank=True, help_text="Elevation in meters")
    
    # Trip details
    min_days = models.PositiveIntegerField(help_text="Minimum days required")
    max_days = models.PositiveIntegerField(null=True, blank=True)
    expected_cost_min = models.DecimalField(max_digits=10, decimal_places=2, help_text="In NPR")
    expected_cost_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='MODERATE')
    best_season = models.CharField(max_length=100, blank=True)  # e.g., "March-May, September-November"
    
    # Media
    cover_image = models.ImageField(upload_to='destinations/')
    video_url = models.URLField(blank=True, null=True)
    has_360_view = models.BooleanField(default=False)
    
    # SEO
    meta_description = models.TextField(max_length=160, blank=True)
    
    # Stats
    view_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, related_name='created_destinations')

    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DestinationImage(models.Model):
    """
    Additional images for destinations.
    Normalized for multiple images per destination.
    """
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='destination_images/')
    caption = models.CharField(max_length=255, blank=True)
    is_360 = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-uploaded_at']

    def __str__(self):
        return f"Image for {self.destination.name}"


class Itinerary(models.Model):
    """
    Manually created itineraries for destinations.
    AI-generated itineraries can be stored temporarily or separately.
    """
    
    SOURCE_CHOICES = [
        ('ADMIN', 'Admin Created'),
        ('AI', 'AI Generated'),
        ('USER', 'User Customized'),
    ]
    
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='itineraries')
    title = models.CharField(max_length=255)
    duration_days = models.PositiveIntegerField()
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='ADMIN')
    
    # If user-customized or AI-generated
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    
    is_default = models.BooleanField(default=False)  # Default itinerary to show
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Itineraries"
        ordering = ['-is_default', 'duration_days']

    def __str__(self):
        return f"{self.title} ({self.duration_days} days) - {self.destination.name}"


class ItineraryDay(models.Model):
    """
    Day-by-day breakdown of an itinerary.
    Normalized to separate table for flexibility.
    """
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='days')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Optional location for that day
    location_name = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Walking/trekking distance
    distance_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    meals_included = models.CharField(max_length=100, blank=True)  # e.g., "Breakfast, Lunch, Dinner"
    accommodation_type = models.CharField(max_length=100, blank=True)  # e.g., "Teahouse", "Camping"

    class Meta:
        ordering = ['itinerary', 'day_number']
        unique_together = ['itinerary', 'day_number']

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"