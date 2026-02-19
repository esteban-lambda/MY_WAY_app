from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Task, TaskComment
from core.rbac_mixins import RBACModelAdminMixin, RestrictExportMixin
from django.utils.html import format_html


class TaskCommentInline(TabularInline):
    model = TaskComment
    extra = 0
    fields = ('user', 'comment', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Task)
class TaskAdmin(RBACModelAdminMixin, RestrictExportMixin, ModelAdmin):
    list_display = (
        'title',
        'priority_badge',
        'status_badge',
        'task_type',
        'assigned_to',
        'due_date',
        'is_overdue_badge'
    )
    list_filter = ('status', 'priority', 'task_type', 'assigned_to', 'due_date')
    search_fields = ('title', 'description', 'account__name', 'contact__first_name', 'contact__last_name')
    date_hierarchy = 'due_date'
    list_select_related = ('assigned_to', 'created_by', 'account', 'contact', 'deal')
    inlines = [TaskCommentInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'task_type', 'priority', 'status')
        }),
        ('Asignación', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Relaciones', {
            'fields': ('account', 'contact', 'deal'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('due_date', 'completed_at', 'reminder_minutes', 'reminder_sent')
        }),
    )
    readonly_fields = ('completed_at',)
    autocomplete_fields = ['account', 'contact', 'deal']
    
    def priority_badge(self, obj):
        colors = {
            'low': '#64748b',
            'medium': '#0ea5e9',
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
    
    def status_badge(self, obj):
        colors = {
            'pending': '#64748b',
            'in_progress': '#0ea5e9',
            'completed': '#10b981',
            'cancelled': '#ef4444',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
            colors.get(obj.status, '#64748b'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def is_overdue_badge(self, obj):
        if obj.is_overdue():
            return format_html(
                '<span style="background-color: #ef4444; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: 600;">⚠️ VENCIDA</span>'
            )
        return '-'
    is_overdue_badge.short_description = 'Estado'


@admin.register(TaskComment)
class TaskCommentAdmin(ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('comment', 'task__title')
    date_hierarchy = 'created_at'
