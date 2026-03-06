from django.contrib import admin
from .models import Customer, MenPerfume, WomenPerfume, Order, Review, WishlistItem, Articles, ContactUS

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_distributor', 'date_created')
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(MenPerfume)
class MenPerfumeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'scent', 'date')
    search_fields = ('name', 'scent')
    list_filter = ('scent',)

@admin.register(WomenPerfume)
class WomenPerfumeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'scent', 'date')
    search_fields = ('name', 'scent')
    list_filter = ('scent',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'billing_name', 'status', 'total', 'date_created')
    list_filter = ('status', 'date_created')
    search_fields = ('billing_name', 'confirmed_order_code')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')

# Basic registrations for the rest
admin.site.register(Articles)
admin.site.register(ContactUS)