from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Define a manager for user model with no username field."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser): 
    USER_TYPE_CHOICES = [
        ('TOURIST', 'Tourist'),
        ('TRAVEL_BUSINESS', 'Travel Business'),
        ('LOCAL_BUSINESS', 'Local Business'),
        ('MANUFACTURER', 'Local Manufacturer'),
        ('ADMIN', 'Admin'),
    ]
    
    username = None
    email = models.EmailField(_("email address"), unique=True)
    contact = models.CharField(max_length=15, blank=True, null=True)  # Made optional
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='TOURIST')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"
    
    @property
    def is_business_user(self):
        """Helper property to check if user is any type of business"""
        return self.user_type in ['TRAVEL_BUSINESS', 'LOCAL_BUSINESS', 'MANUFACTURER']
    
    @property
    def is_travel_business(self):
        return self.user_type == 'TRAVEL_BUSINESS'
    
    @property
    def is_local_business(self):
        return self.user_type == 'LOCAL_BUSINESS'
    
    @property
    def is_manufacturer(self):
        return self.user_type == 'MANUFACTURER'
    
    @property
    def is_admin(self):
        return self.user_type == 'ADMIN'

