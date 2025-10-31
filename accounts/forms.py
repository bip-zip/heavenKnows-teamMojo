from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth import authenticate

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-12 pr-4 py-3 bg-white rounded-xl border border-gray-200 focus-ring',
            'placeholder': 'First Name',
        })
    )
    last_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-12 pr-4 py-3 bg-white rounded-xl border border-gray-200 focus-ring',
            'placeholder': 'Last Name',
        })
    )
    contact = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-12 pr-4 py-3 bg-white rounded-xl border border-gray-200 focus-ring',
            'placeholder': '+977-9800000000',
        })
    )
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'w-full pl-12 pr-4 py-3 bg-white rounded-xl border border-gray-200 focus-ring',
            'placeholder': 'you@example.com',
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full pl-12 pr-4 py-3 bg-white rounded-xl border border-gray-200 focus-ring',
            'placeholder': 'Password',
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full pl-12 pr-4 py-3 bg-white rounded-xl border border-gray-200 focus-ring',
            'placeholder': 'Confirm Password',
        })
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'contact', 'email')




class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'autofocus': True, 'class':'w-full pl-12 pr-4 py-3 bg-white rounded-xl border border-gray-200 focus-ring', 'placeholder':"Email Address"}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class':'w-full pl-12 pr-4 py-3 bg-white rounded-xl border border-gray-200 focus-ring', 'placeholder':'Password'}))
    

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")
        return self.cleaned_data

# class BusinessRegisterForm(UserCreationForm):
#     # Business fields
#     business_name = forms.CharField(max_length=255)
#     pan_or_vat = forms.CharField(max_length=50)
#     document = forms.FileField()
#     request_letter = forms.FileField()

#     class Meta:
#         model = CustomUser
#         fields = ('email', 'contact', 'password1', 'password2')

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.is_business = True
#         user.is_local = False
#         if commit:
#             user.save()

#             BusinessInfo.objects.create(
#                 user=user,
#                 business_name=self.cleaned_data['business_name'],
#                 pan_or_vat=self.cleaned_data['pan_or_vat'],
#                 document=self.cleaned_data['document'],
#                 request_letter=self.cleaned_data['request_letter'],
#             )
#         return user