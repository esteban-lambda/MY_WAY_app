from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Notification
from django.utils.html import format_html


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = (
        'title',
        'notification_type',
        'priority_badge',
        'recipient',
        'is_read_badge',
        'created_at'
    )
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username', 'recipient__email')
    date_hierarchy = 'created_at'
    list_select_related = ('recipient', 'task', 'deal', 'account', 'contact')
    
    fieldsets = (
        ('Información de la Notificación', {
            'fields': ('recipient', 'notification_type', 'priority', 'title', 'message', 'action_url')
        }),
        ('Estado', {
            'fields': ('is_read', 'read_at', 'expires_at')
        }),
        ('Relaciones', {
            'fields': ('task', 'deal', 'account', 'contact'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('read_at', 'created_at')
    
    def priority_badge(self, obj):
        colors = {
            'low': '#64748b',
            'normal': '#0ea5e9',
            'high': '#f97316',
            'urgent': '#ef4444',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
            colors.get(obj.priority, '#64748b'),
            obj.get_priority_display().upper()
        )
    priority_badge.short_description = 'Prioridad'
    
    def is_read_badge(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="color: #10b981; font-weight: 600;">✓ Leída</span>'
            )
        return format_html(
            '<span style="color: #ef4444; font-weight: 600;">• No leída</span>'
        )
    is_read_badge.short_description = 'Estado'
