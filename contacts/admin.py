from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from core.rbac_mixins import RBACModelAdminMixin, RestrictExportMixin
from .models import Contact


class ContactInteractionInline(TabularInline):
    """Inline para mostrar interacciones del contacto"""
    from interactions.models import Interaction
    model = Interaction
    fk_name = 'contact'
    extra = 0
    can_delete = False
    fields = ('interaction_type', 'direction', 'subject', 'scheduled_at', 'status', 'assigned_to')
    readonly_fields = ('interaction_type', 'direction', 'subject', 'scheduled_at', 'status')
    ordering = ['-scheduled_at']


@admin.register(Contact)
class ContactAdmin(RBACModelAdminMixin, RestrictExportMixin, ModelAdmin):
    list_display = ("full_name", "account", "job_title", "email", "phone", "interaction_count")
    list_filter = ("account",)
    search_fields = ("first_name", "last_name", "email", "account__name")
    list_select_related = ("account",)
    inlines = [ContactInteractionInline]
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'job_title')
        }),
        ('Información Empresarial', {
            'fields': ('account',)
        }),
        ('Próximo Contacto', {
            'fields': ('next_contact_date',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('next_contact_date',)
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Nombre Completo'
    
    def interaction_count(self, obj):
        count = obj.interactions.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #64748b; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 12px;">{}</span>',
                count
            )
        return '-'
    interaction_count.short_description = 'Interacciones'
    
    def next_contact_date(self, obj):
        """Calcula y muestra la próxima fecha de contacto sugerida"""
        from interactions.models import Interaction
        next_date = Interaction.calculate_next_contact_date(contact=obj)
        if next_date:
            return format_html(
                '<span style="background-color: #0ea5e9; color: white; padding: 8px 15px; '
                'border-radius: 5px; font-weight: bold;">{}</span>',
                next_date.strftime('%d/%m/%Y')
            )
        return '-'
    next_contact_date.short_description = 'Próximo Contacto Sugerido'