from django import forms
from .models import TourPackage, PackageItinerary
from destinations.models import Destination


class TourPackageForm(forms.ModelForm):
    """Form for creating/editing tour packages"""
    
    destinations = forms.ModelMultipleChoiceField(
        queryset=Destination.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={
            'class': 'hidden',
            'id': 'destination-select'
        }),
        required=True
    )
    
    class Meta:
        model = TourPackage
        fields = [
            'title', 'description', 'destinations', 'duration_days', 'duration_nights',
            'price_per_person', 'group_size_min', 'group_size_max',
            'inclusions', 'exclusions', 'available_from', 'available_to',
            'cover_image', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'placeholder': 'Enter package title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'rows': 4,
                'placeholder': 'Describe your package...'
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'min': 1
            }),
            'duration_nights': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'min': 0
            }),
            'price_per_person': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'step': '0.01',
                'placeholder': 'Price in NPR'
            }),
            'group_size_min': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'min': 1
            }),
            'group_size_max': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'min': 1
            }),
            'inclusions': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'rows': 4,
                'placeholder': 'List what is included (one per line)'
            }),
            'exclusions': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'rows': 4,
                'placeholder': 'List what is not included (one per line)'
            }),
            'available_from': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'type': 'date'
            }),
            'available_to': forms.DateInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3',
                'type': 'date'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
                'accept': 'image/*'
            }),
            'status': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-3'
            })
        }