from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Replace UserAdmin defaults with fields that exist in your CustomUser
    list_display = ('email', 'contact', 'is_superuser')
    list_filter = ('is_superuser', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('contact',)}),
        ('user_type', {'fields': ('user_type',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'contact', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser')}
        ),
    )

    search_fields = ('email', 'contact')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
