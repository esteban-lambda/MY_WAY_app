from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin, TabularInline
from core.rbac_mixins import RBACModelAdminMixin, RestrictExportMixin
from .models import Account, UserProfile


class AccountInteractionInline(TabularInline):
    """Inline para mostrar interacciones de la empresa"""
    from interactions.models import Interaction
    model = Interaction
    fk_name = 'account'
    extra = 0
    can_delete = False
    fields = ('interaction_type', 'direction', 'contact', 'subject', 'scheduled_at', 'status')
    readonly_fields = ('interaction_type', 'direction', 'contact', 'subject', 'scheduled_at', 'status')
    ordering = ['-scheduled_at']


@admin.register(Account)
class AccountAdmin(RBACModelAdminMixin, RestrictExportMixin, ModelAdmin):
    list_display = ("name", "industry", "created_at", "interaction_count")
    search_fields = ("name", "industry")
    list_filter = ("industry",)
    inlines = [AccountInteractionInline]
    
    def interaction_count(self, obj):
        from django.utils.html import format_html
        count = obj.interactions.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #547792; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 12px; font-weight: 600;">{}</span>',
                count
            )
        return '-'
    interaction_count.short_description = 'Interacciones'


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'
    fields = ('role', 'phone', 'department', 'created_by', 'is_active')


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')
    
    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return '-'
    get_role.short_description = 'Rol'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)