from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('MoSPI & Cadre Information', {
            'fields': ('cadre', 'designation', 'department_wing', 'employee_code', 'igot_user_id', 'role')
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'cadre', 'designation', 'department_wing', 'role')
    list_filter = ('cadre', 'department_wing', 'role', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'employee_code', 'igot_user_id')
