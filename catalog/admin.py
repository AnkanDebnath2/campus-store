from django.contrib import admin
from .models import Author, Category, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'price')
    list_filter = ('category', 'author')
    search_fields = ('title', 'author__name')
    fields = ('title', 'author', 'category', 'price', 'description', 'cover_image')
