from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


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


