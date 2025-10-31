from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import CustomUser


class BusinessProfile(models.Model):
    
    BUSINESS_TYPE_CHOICES = [
        ('TRAVEL_AGENCY', 'Travel Agency'),
        ('HOTEL', 'Hotel'),
        ('HOMESTAY', 'Homestay'),
        ('RESTAURANT', 'Restaurant'),
        ('MANUFACTURER', 'Product Manufacturer'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='business_profile')
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES)
    
    # Registration details
    pan_or_vat = models.CharField(max_length=50, unique=True)
    logo = models.ImageField(upload_to='business_logos/')
    registration_document = models.FileField(upload_to='business_docs/')
    request_letter = models.FileField(upload_to='request_letters/')
    
    # Location details
    address = models.TextField()
    district = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Business details
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=15)
    website = models.URLField(blank=True, null=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_businesses')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Business Profile"
        verbose_name_plural = "Business Profiles"

    def __str__(self):
        return f"{self.business_name} ({self.get_business_type_display()})"
    

class AccommodationDetails(models.Model):
    """
    Additional details for hotels and homestays.
    Separated from BusinessProfile for normalization (only relevant for accommodation businesses).
    """
    business = models.OneToOneField(BusinessProfile, on_delete=models.CASCADE, related_name='accommodation_details')
    
    total_rooms = models.PositiveIntegerField()
    price_range_min = models.DecimalField(max_digits=10, decimal_places=2)
    price_range_max = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Amenities (using comma-separated or JSONField would work, keeping it simple)
    has_wifi = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_restaurant = models.BooleanField(default=False)
    
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Accommodation details for {self.business.business_name}"


class ManufacturerDetails(models.Model):
    """
    Additional details for local product manufacturers.
    Separated for normalization (only relevant for manufacturers).
    """
    
    PRODUCT_CATEGORY_CHOICES = [
        ('TEXTILES', 'Textiles & Wool'),
        ('FOOD', 'Food Products'),
        ('HANDICRAFTS', 'Handicrafts'),
        ('JEWELRY', 'Jewelry'),
        ('OTHER', 'Other'),
    ]
    
    business = models.OneToOneField(BusinessProfile, on_delete=models.CASCADE, related_name='manufacturer_details')
    product_category = models.CharField(max_length=20, choices=PRODUCT_CATEGORY_CHOICES)
    product_description = models.TextField()
    minimum_order_quantity = models.PositiveIntegerField(null=True, blank=True)
    ships_internationally = models.BooleanField(default=False)

    def __str__(self):
        return f"Manufacturer details for {self.business.business_name}"


class BusinessImage(models.Model):
    """
    Images for businesses (gallery).
    Normalized in separate table for multiple images per business.
    """
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='business_images/')
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-uploaded_at']

    def __str__(self):
        return f"Image for {self.business.business_name}"