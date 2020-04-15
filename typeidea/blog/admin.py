from django.contrib import admin
from blog.models import Post, Category, Tag


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'is_nav', 'created_time']
    fields = ['name', 'status', 'is_nav']
