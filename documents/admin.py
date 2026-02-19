from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import Document


@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ['icon_display', 'name', 'type_badge', 'file_size_display', 
                    'account', 'contact', 'deal', 'confidential_badge', 'uploaded_by', 'uploaded_at']
    list_filter = ['document_type', 'is_confidential', 'uploaded_at']
    search_fields = ['name', 'description', 'file']
    readonly_fields = ['file_size', 'uploaded_at', 'updated_at', 'get_file_extension', 'get_file_size_display']
    
    fieldsets = [
        ('Información del Documento', {
            'fields': ['name', 'document_type', 'description', 'file']
        }),
        ('Relacionado con', {
            'fields': ['account', 'contact', 'deal']
        }),
        ('Metadata', {
            'fields': ['uploaded_by', 'uploaded_at', 'updated_at', 'file_size', 'get_file_extension', 'get_file_size_display']
        }),
        ('Seguridad', {
            'fields': ['is_confidential']
        }),
    ]
    
    def icon_display(self, obj):
        """Muestra el ícono según la extensión del archivo"""
        icons = {
            'PDF': '📕',
            'DOC': '📘',
            'DOCX': '📘',
            'XLS': '📗',
            'XLSX': '📗',
            'PPT': '📙',
            'PPTX': '📙',
            'TXT': '📄',
            'CSV': '📊',
            'JPG': '🖼️',
            'JPEG': '🖼️',
            'PNG': '🖼️',
        }
        ext = obj.get_file_extension()
        return format_html('<span style="font-size: 20px;">{}</span>', icons.get(ext, '📎'))
    icon_display.short_description = 'Tipo'
    
    def type_badge(self, obj):
        """Badge del tipo de documento"""
        colors = {
            'contract': '#10b981',
            'proposal': '#3b82f6',
            'invoice': '#f59e0b',
            'quote': '#14b8a6',
            'report': '#8b5cf6',
            'presentation': '#ec4899',
            'other': '#64748b',
        }
        color = colors.get(obj.document_type, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-size: 11px; font-weight: 500;">{}</span>',
            color,
            obj.get_document_type_display()
        )
    type_badge.short_description = 'Categoría'
    
    def file_size_display(self, obj):
        """Muestra el tamaño del archivo"""
        return obj.get_file_size_display()
    file_size_display.short_description = 'Tamaño'
    
    def confidential_badge(self, obj):
        """Badge de confidencialidad"""
        if obj.is_confidential:
            return format_html(
                '<span style="background-color: #ef4444; color: white; padding: 3px 10px; '
                'border-radius: 4px; font-size: 11px; font-weight: 500;">🔒 Confidencial</span>'
            )
        return ''
    confidential_badge.short_description = 'Seguridad'
