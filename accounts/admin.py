from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'full_name_display', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Clinical Info', {'fields': ('role', 'phone', 'department', 'license_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Clinical Info', {'fields': ('role', 'phone', 'department')}),
    )

    def full_name_display(self, obj):
        return obj.get_full_name() or '—'
    full_name_display.short_description = 'Full Name'
