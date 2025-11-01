
from django import forms
from django.contrib.auth import get_user_model
from .models import BusinessProfile

User = get_user_model()


class BusinessRegistrationForm(forms.ModelForm):
    """Simplified form for initial business registration"""
    
    # User fields
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
            'placeholder': 'business@example.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
            'placeholder': '••••••••'
        }),
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
            'placeholder': '••••••••'
        })
    )
    contact = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
            'placeholder': '+977-9800000000'
        })
    )
    
    class Meta:
        model = BusinessProfile
        fields = ['business_name', 'business_type', 'pan_or_vat', 'registration_document', 
                  'request_letter', 'address', 'district', 'province', 'phone', 'website', 'description']
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
                'placeholder': 'Your Business Name'
            }),
            'business_type': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3'
            }),
            'pan_or_vat': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
                'placeholder': 'Enter your PAN or VAT number'
            }),
            'registration_document': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'request_letter': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'address': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
                'rows': 3,
                'placeholder': 'Street address, locality'
            }),
            'district': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
                'placeholder': 'e.g., Kathmandu'
            }),
            'province': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
                'placeholder': 'e.g., Bagmati'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
                'placeholder': 'Business phone number'
            }),
            'website': forms.URLInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
                'placeholder': 'https://www.yourbusiness.com'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 px-4 py-3',
                'rows': 4,
                'placeholder': 'Tell us about your business...'
            })
        }
        labels = {
            'pan_or_vat': 'PAN/VAT Number',
            'registration_document': 'Registration Document',
            'request_letter': 'Request Letter',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        # Check password match
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
from .models import AccommodationDetails, ManufacturerDetails, BusinessImage


class AccommodationDetailsForm(forms.ModelForm):
    """Form for accommodation details"""
    
    class Meta:
        model = AccommodationDetails
        fields = ['total_rooms', 'price_range_min', 'price_range_max', 
                  'has_wifi', 'has_parking', 'has_restaurant', 'check_in_time', 'check_out_time']
        widgets = {
            'total_rooms': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'min': 1
            }),
            'price_range_min': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'step': '0.01',
                'placeholder': 'Minimum price in NPR'
            }),
            'price_range_max': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'step': '0.01',
                'placeholder': 'Maximum price in NPR'
            }),
            'has_wifi': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            }),
            'has_parking': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            }),
            'has_restaurant': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            }),
            'check_in_time': forms.TimeInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'type': 'time'
            }),
            'check_out_time': forms.TimeInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'type': 'time'
            })
        }


class ManufacturerDetailsForm(forms.ModelForm):
    """Form for manufacturer details"""
    
    class Meta:
        model = ManufacturerDetails
        fields = ['product_category', 'product_description', 'minimum_order_quantity', 'ships_internationally']
        widgets = {
            'product_category': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3'
            }),
            'product_description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'rows': 4,
                'placeholder': 'Describe your products in detail...'
            }),
            'minimum_order_quantity': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'min': 1,
                'placeholder': 'Minimum order quantity (optional)'
            }),
            'ships_internationally': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            })
        }


class BusinessImageForm(forms.ModelForm):
    """Form for uploading business images"""
    
    class Meta:
        model = BusinessImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'placeholder': 'Image caption (optional)'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            })
        }