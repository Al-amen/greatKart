from django.contrib import admin

from .models import Product, Variation,ReviewRating

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'is_available', 'slug', 'created_date', 'modified_date')
    prepopulated_fields = {'slug': ('product_name',)}
    list_editable = ('price', 'stock', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('product_name',)
    list_per_page = 10
admin.site.register(Product, ProductAdmin)


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active')
    search_fields = ('product__product_name',)
admin.site.register(Variation, VariationAdmin)

class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'subject', 'review', 'rating', 'ip', 'status','created_date','updated_date')
    list_filter = ('product', 'user', 'rating', 'status')
    search_fields = ('product__product_name', 'user__username')
    list_editable = ('status',)
    actions = ['approve_reviews']
    def approve_reviews(self, request, queryset):
        for review in queryset:
            review.status = True
            review.save()
        self.message_user(request, "Selected reviews have been approved.")
    approve_reviews.short_description = "Approve selected reviews"
admin.site.register(ReviewRating, ReviewRatingAdmin)