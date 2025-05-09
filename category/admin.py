from django.contrib import admin

from .models import Category

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name", "slug", "description", "cat_image")
    prepopulated_fields = {"slug": ("category_name",)}
    search_fields = ("category_name",)
    list_per_page = 10
    list_filter = ("category_name",)
    ordering = ("id",)


admin.site.register(Category, CategoryAdmin)
