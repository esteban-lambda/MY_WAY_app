from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from core.rbac_mixins import RBACModelAdminMixin, RestrictExportMixin
from .models import Interaction, Call, Meeting


class CallInline(admin.StackedInline):
    model = Call
    extra = 0
    can_delete = False


class MeetingInline(admin.StackedInline):
    model = Meeting
    extra = 0
    can_delete = False
    filter_horizontal = ('attendees',)


@admin.register(Interaction)
class InteractionAdmin(RBACModelAdminMixin, RestrictExportMixin, ModelAdmin):
    list_display = (
        'subject',
        'interaction_type_badge',
        'direction_badge',
        'account', 
        'contact', 
        'assigned_to', 
        'scheduled_at', 
        'status_badge'
    )
    list_filter = ('interaction_type', 'direction', 'status', 'scheduled_at', 'assigned_to')
    search_fields = ('subject', 'summary', 'account__name', 'contact__first_name', 'contact__last_name')
    date_hierarchy = 'scheduled_at'
    list_select_related = ('account', 'contact', 'deal', 'assigned_to')
    autocomplete_fields = ['contact', 'deal']
    
    fieldsets = (
        ('Información General', {
            'fields': ('interaction_type', 'direction', 'subject', 'summary', 'description', 'status')
        }),
        ('Relaciones', {
            'fields': ('account', 'contact', 'deal', 'assigned_to')
        }),
        ('Detalles de Tiempo', {
            'fields': ('scheduled_at', 'duration_minutes', 'next_contact_suggestion')
        }),
        ('Notas y Resultado', {
            'fields': ('notes', 'outcome')
        }),
    )
    readonly_fields = ('next_contact_suggestion',)
    
    def interaction_type_badge(self, obj):
        colors = {
            'call': '#1e293b',
            'meeting': '#64748b',
            'email': '#0ea5e9',
            'note': '#f1f5f9'
        }
        icons = {
            'call': 'CALL',
            'meeting': 'MTG',
            'email': 'EMAIL',
            'note': 'NOTE'
        }
        color = colors.get(obj.interaction_type, '#999')
        icon = icons.get(obj.interaction_type, '')
        text_color = 'white' if obj.interaction_type != 'note' else '#1e293b'
        
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 10px; '
            'border-radius: 12px; font-size: 12px; font-weight: 600;">{} {}</span>',
            color, text_color, icon, obj.get_interaction_type_display()
        )
    interaction_type_badge.short_description = 'Tipo'
    interaction_type_badge.admin_order_field = 'interaction_type'
    
    def direction_badge(self, obj):
        colors = {
            'inbound': '#28a745',
            'outbound': '#007bff',
            'internal': '#6c757d'
        }
        arrows = {
            'inbound': 'IN',
            'outbound': 'OUT',
            'internal': 'INT'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 8px; font-size: 11px;">{} {}</span>',
            colors.get(obj.direction, '#999'),
            arrows.get(obj.direction, ''),
            obj.get_direction_display()
        )
    direction_badge.short_description = 'Dirección'
    direction_badge.admin_order_field = 'direction'
    
    def status_badge(self, obj):
        colors = {
            'scheduled': '#ffc107',
            'completed': '#28a745',
            'cancelled': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 8px; font-size: 11px; font-weight: 600;">{}</span>',
            colors.get(obj.status, '#999'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    def next_contact_suggestion(self, obj):
        """Muestra la próxima fecha de contacto sugerida"""
        next_date = obj.get_next_suggested_contact()
        if next_date:
            return format_html(
                '<div style="background: linear-gradient(135deg, #1e293b 0%, #64748b 100%); '
                'color: white; padding: 15px; border-radius: 8px; text-align: center;">'
                '<strong>Próximo Contacto Sugerido:</strong><br>'
                '<span style="font-size: 18px; font-weight: bold;">{}</span></div>',
                next_date.strftime('%d de %B, %Y')
            )
        return '-'
    next_contact_suggestion.short_description = 'Próximo Contacto'
    
    def get_inlines(self, request, obj=None):
        if obj and obj.interaction_type == 'call':
            return [CallInline]
        elif obj and obj.interaction_type == 'meeting':
            return [MeetingInline]
        return []


@admin.register(Call)
class CallAdmin(ModelAdmin):
    list_display = ('interaction', 'phone_number', 'direction', 'call_outcome')
    list_filter = ('direction', 'call_outcome')
    search_fields = ('phone_number', 'interaction__subject')


@admin.register(Meeting)
class MeetingAdmin(ModelAdmin):
    list_display = ('interaction', 'meeting_type', 'location')
    list_filter = ('meeting_type',)
    search_fields = ('location', 'interaction__subject')
    filter_horizontal = ('attendees',)
