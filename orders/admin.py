from django.contrib import admin
from .models import Order, Review


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_id', 'user_name', 'quantity', 'total', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('book_id',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_id', 'reviewer_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('book_id', 'reviewer_name', 'comment')
