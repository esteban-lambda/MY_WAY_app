from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import EmailTemplate, EmailLog
from core.rbac_mixins import RestrictExportMixin
from django.utils.html import format_html


@admin.register(EmailTemplate)
class EmailTemplateAdmin(RestrictExportMixin, ModelAdmin):
    list_display = ('name', 'category', 'subject', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'subject', 'body_html', 'body_text')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'category', 'is_active')
        }),
        ('Contenido del Email', {
            'fields': ('subject', 'body_html', 'body_text')
        }),
        ('Variables', {
            'fields': ('available_variables',),
            'description': 'Variables disponibles: {{contact_name}}, {{contact_email}}, {{account_name}}, {{user_name}}, {{deal_value}}'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmailLog)
class EmailLogAdmin(RestrictExportMixin, ModelAdmin):
    list_display = (
        'subject',
        'to_email',
        'status_badge',
        'sent_at',
        'opened_at',
        'sent_by'
    )
    list_filter = ('status', 'sent_at', 'sent_by')
    search_fields = ('subject', 'to_email', 'from_email', 'body_text')
    date_hierarchy = 'sent_at'
    list_select_related = ('template', 'sent_by', 'account', 'contact', 'deal')
    
    fieldsets = (
        ('Información del Email', {
            'fields': ('template', 'to_email', 'from_email', 'subject')
        }),
        ('Contenido', {
            'fields': ('body_html', 'body_text'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('status', 'sent_at', 'opened_at', 'clicked_at', 'error_message')
        }),
        ('Relaciones', {
            'fields': ('sent_by', 'account', 'contact', 'deal'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('sent_at', 'opened_at', 'clicked_at', 'created_at')
    
    def status_badge(self, obj):
        colors = {
            'pending': '#64748b',
            'sent': '#0ea5e9',
            'failed': '#ef4444',
            'opened': '#10b981',
            'clicked': '#8b5cf6',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
            colors.get(obj.status, '#64748b'),
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Estado'
