from django.contrib import admin
from .models import (
    Category, Tag, Destination, DestinationImage,
    Itinerary, ItineraryDay
)


# ---------- CATEGORY ADMIN ----------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    ordering = ('name',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'icon', 'image')
        }),
        ('Metadata', {
            'fields': ('created_at',),
        }),
    )


# ---------- TAG ADMIN ----------
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('name',)


# ---------- INLINE MODELS ----------
class DestinationImageInline(admin.TabularInline):
    model = DestinationImage
    extra = 1
    fields = ('image', 'caption', 'is_360', 'order')
    ordering = ('order',)
    show_change_link = True


class ItineraryInline(admin.TabularInline):
    model = Itinerary
    extra = 0
    fields = ('title', 'duration_days', 'source', 'is_default')
    show_change_link = True


# ---------- DESTINATION ADMIN ----------
@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'district', 'province',
        'difficulty', 'is_featured', 'is_active', 'created_at'
    )
    list_filter = (
        'category', 'difficulty', 'is_featured', 'is_active', 'province'
    )
    search_fields = ('name', 'district', 'province', 'short_description', 'full_description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DestinationImageInline, ItineraryInline]
    readonly_fields = ('created_at', 'updated_at', 'view_count')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('category', 'tags', 'created_by')
    list_editable = ('is_featured', 'is_active')
    ordering = ('-is_featured', '-created_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'tags', 'short_description', 'full_description')
        }),
        ('Location', {
            'fields': (
                ('district', 'province'),
                ('latitude', 'longitude', 'elevation'),
            )
        }),
        ('Trip Details', {
            'fields': (
                ('min_days', 'max_days'),
                ('expected_cost_min', 'expected_cost_max'),
                'difficulty', 'best_season'
            )
        }),
        ('Media & SEO', {
            'fields': ('cover_image', 'video_url', 'has_360_view', 'meta_description')
        }),
        ('Statistics', {
            'fields': ('view_count', 'is_featured', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


# ---------- ITINERARY DAY INLINE ----------
class ItineraryDayInline(admin.TabularInline):
    model = ItineraryDay
    extra = 0
    fields = (
        'day_number', 'title', 'description', 'location_name',
        ('latitude', 'longitude'),
        ('distance_km', 'estimated_hours'),
        ('meals_included', 'accommodation_type'),
    )
    ordering = ('day_number',)


# ---------- ITINERARY ADMIN ----------
@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'duration_days', 'source', 'is_default', 'created_at')
    list_filter = ('source', 'is_default', 'destination')
    search_fields = ('title', 'destination__name')
    autocomplete_fields = ('destination', 'created_by')
    inlines = [ItineraryDayInline]
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-is_default', 'destination')

    fieldsets = (
        ('Basic Info', {
            'fields': ('destination', 'title', 'duration_days', 'source')
        }),
        ('Additional Info', {
            'fields': ('created_by', 'is_default')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# ---------- ITINERARY DAY ADMIN ----------
@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):
    list_display = ('itinerary', 'day_number', 'title', 'location_name', 'distance_km', 'estimated_hours')
    list_filter = ('itinerary',)
    search_fields = ('title', 'itinerary__title', 'description', 'location_name')
    ordering = ('itinerary', 'day_number')
    autocomplete_fields = ('itinerary',)
