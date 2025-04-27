from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,UserProfile
from django.utils.html import format_html


class CustomUserAdmin(UserAdmin):
    list_display = ('id','email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff','last_login','date_joined')
    list_display_links = ('email','username','first_name','last_name')
    list_filter = ('is_admin',)
  
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_per_page = 10
    add_fieldsets = ()
    remove_fieldsets = ()
    fieldsets = ()
admin.site.register(CustomUser, CustomUserAdmin)



class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'division', 'district', 'country')

admin.site.register(UserProfile,UserProfileAdmin)