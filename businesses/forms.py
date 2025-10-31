
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