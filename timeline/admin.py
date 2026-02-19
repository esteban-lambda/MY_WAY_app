from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import TimelineEvent


@admin.register(TimelineEvent)
class TimelineEventAdmin(ModelAdmin):
    list_display = ['icon_display', 'title', 'event_type_badge', 'action_badge', 
                    'user', 'related_display', 'important_badge', 'created_at']
    list_filter = ['event_type', 'action', 'is_important', 'is_public', 'created_at', 'user']
    search_fields = ['title', 'description', 'metadata']
    readonly_fields = ['icon_display', 'created_at', 'content_type', 'object_id']
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Información del Evento', {
            'fields': ['event_type', 'action', 'title', 'description', 'icon_display']
        }),
        ('Relacionado con', {
            'fields': ['content_type', 'object_id', 'account', 'contact', 'deal']
        }),
        ('Usuario y Metadata', {
            'fields': ['user', 'metadata', 'created_at']
        }),
        ('Configuración', {
            'fields': ['is_public', 'is_important']
        }),
    ]
    
    def icon_display(self, obj):
        """Muestra el icono del evento"""
        return format_html(
            '<span style="font-size: 20px;">{}</span>',
            obj.get_icon()
        )
    icon_display.short_description = 'Icono'
    
    def event_type_badge(self, obj):
        """Badge del tipo de evento"""
        color = obj.get_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-size: 11px; font-weight: 500;">{}</span>',
            color,
            obj.get_event_type_display()
        )
    event_type_badge.short_description = 'Tipo'
    
    def action_badge(self, obj):
        """Badge de la acción"""
        action_colors = {
            'created': '#10b981',
            'updated': '#3b82f6',
            'deleted': '#ef4444',
            'completed': '#10b981',
            'sent': '#0ea5e9',
            'won': '#22c55e',
            'lost': '#ef4444',
            'accepted': '#10b981',
            'rejected': '#ef4444',
        }
        color = action_colors.get(obj.action, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-size: 11px; font-weight: 500;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'Acción'
    
    def related_display(self, obj):
        """Muestra las relaciones"""
        parts = []
        if obj.account:
            parts.append(f"🏢 {obj.account.name}")
        if obj.contact:
            parts.append(f"👤 {obj.contact.first_name} {obj.contact.last_name}")
        if obj.deal:
            parts.append(f"💼 {obj.deal.name}")
        return format_html('<br>'.join(parts)) if parts else '-'
    related_display.short_description = 'Relacionado'
    
    def important_badge(self, obj):
        """Indica si es importante"""
        if obj.is_important:
            return format_html(
                '<span style="color: #ef4444; font-size: 16px;">⭐</span>'
            )
        return ''
    important_badge.short_description = 'Importante'
    
    def has_add_permission(self, request):
        """No permitir crear eventos manualmente (se crean automáticamente)"""
        return False
