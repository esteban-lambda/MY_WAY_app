from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from simple_history.admin import SimpleHistoryAdmin
from core.rbac_mixins import RBACModelAdminMixin, RestrictExportMixin
from .models import Deal, Product, DealProduct, Quote, QuoteItem


class DealProductInline(admin.TabularInline):
    model = DealProduct
    extra = 1
    fields = ('product', 'quantity', 'unit_price', 'discount_percent', 'line_total')
    readonly_fields = ('line_total',)
    autocomplete_fields = ['product']
    
    def line_total(self, obj):
        if obj.pk:
            return f"${obj.get_total():,.2f}"
        return '-'
    line_total.short_description = 'Total Línea'


class DealInteractionInline(TabularInline):
    """Inline para mostrar interacciones del deal"""
    from interactions.models import Interaction
    model = Interaction
    fk_name = 'deal'
    extra = 0
    can_delete = False
    fields = ('interaction_type', 'direction', 'subject', 'scheduled_at', 'status', 'assigned_to')
    readonly_fields = ('interaction_type', 'direction', 'subject', 'scheduled_at', 'status')
    ordering = ['-scheduled_at']


@admin.register(Deal)
class DealAdmin(RBACModelAdminMixin, RestrictExportMixin, ModelAdmin, SimpleHistoryAdmin):
    list_display = (
        "name", 
        "account", 
        "value",
        "weighted_value_column",
        "stage", 
        "lead_score_display",
        "assigned_to", 
        "expected_close_date"
    )
    list_filter = ("stage", "account", "assigned_to", "lead_score")
    search_fields = ("name", "account__name")
    list_editable = ("stage",)
    inlines = [DealProductInline, DealInteractionInline]
    readonly_fields = ('lead_score_badge', 'last_score_update', 'next_contact_date')
    autocomplete_fields = ['account', 'contact']
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'account', 'contact', 'assigned_to')
        }),
        ('Detalles Financieros', {
            'fields': ('value', 'stage', 'expected_close_date')
        }),
        ('Lead Scoring', {
            'fields': ('lead_score_badge', 'last_score_update'),
            'classes': ('collapse',),
            'description': 'Puntuación automática basada en Fit (perfil) y Engagement (actividad)'
        }),
        ('Próximo Contacto', {
            'fields': ('next_contact_date',),
            'classes': ('collapse',),
        }),
    )
    
    def next_contact_date(self, obj):
        """Calcula y muestra la próxima fecha de contacto sugerida para este deal"""
        from interactions.models import Interaction
        next_date = Interaction.calculate_next_contact_date(deal=obj)
        if next_date:
            return format_html(
                '<div style="background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); '
                'color: white; padding: 15px; border-radius: 8px; text-align: center; '
                'font-weight: bold; font-size: 16px;\">'
                'Próximo Contacto Sugerido: {}</div>',
                next_date.strftime('%d de %B, %Y')
            )
        return '-'
    next_contact_date.short_description = 'Próximo Contacto'
    
    def lead_score_display(self, obj):
        """Muestra el score con color en la lista"""
        color = obj.get_score_display_color()
        category = obj.get_score_category()
        
        # Indicadores según categoría
        indicators = {
            'hot': 'HOT',
            'warm': 'WARM',
            'cold': 'COLD',
            'frozen': 'FROZEN'
        }
        indicator = indicators.get(category, '')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 15px; font-weight: bold; font-size: 14px;">'
            '{} {}</span>',
            color,
            indicator,
            obj.lead_score
        )
    lead_score_display.short_description = 'Lead Score'
    lead_score_display.admin_order_field = 'lead_score'
    
    def lead_score_badge(self, obj):
        """Muestra el score con detalle en la vista de edición"""
        color = obj.get_score_display_color()
        category = obj.get_score_category()
        
        category_names = {
            'hot': 'HOT LEAD',
            'warm': 'WARM LEAD',
            'cold': 'COLD LEAD',
            'frozen': 'FROZEN LEAD'
        }
        category_name = category_names.get(category, 'Unknown')
        
        return format_html(
            '<div style="background-color: {}; color: white; padding: 20px; '
            'border-radius: 10px; text-align: center; font-size: 18px; '
            'font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'
            '<div style="font-size: 48px; margin-bottom: 10px;">{}</div>'
            '<div style="font-size: 24px;">{}</div>'
            '</div>',
            color,
            obj.lead_score,
            category_name
        )
    lead_score_badge.short_description = 'Puntuación del Lead'
    
    def weighted_value_column(self, obj):
        """Muestra el valor ponderado según probabilidad de cierre"""
        probability = obj.get_probability()
        weighted = obj.weighted_value
        
        # Color según la etapa
        stage_colors = {
            'prospecting': '#999999',
            'negotiation': '#64748b',
            'closed_won': '#2ecc71',
            'closed_lost': '#e74c3c',
        }
        color = stage_colors.get(obj.stage, '#999999')
        
        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-weight: bold; color: {};">${:,.2f}</div>'
            '<div style="font-size: 11px; color: #888;">{}% prob.</div>'
            '</div>',
            color,
            weighted,
            int(probability * 100)
        )
    weighted_value_column.short_description = 'Valor Ponderado'
    weighted_value_column.admin_order_field = 'value'


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'sku', 'category', 'unit_price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'sku', 'description')
    list_editable = ('unit_price', 'is_active')
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('name', 'sku', 'description', 'category')
        }),
        ('Precio y Estado', {
            'fields': ('unit_price', 'is_active')
        }),
    )


@admin.register(DealProduct)
class DealProductAdmin(ModelAdmin):
    list_display = ('deal', 'product', 'quantity', 'unit_price', 'discount_percent', 'get_total')
    list_filter = ('deal__stage', 'product__category')
    search_fields = ('deal__name', 'product__name')
    autocomplete_fields = ['deal', 'product']
    
    def get_total(self, obj):
        return f"${obj.get_total():,.2f}"
    get_total.short_description = 'Total'


class QuoteItemInline(TabularInline):
    model = QuoteItem
    extra = 1
    fields = ('product', 'description', 'quantity', 'unit_price', 'discount_percent', 'line_total', 'order')
    readonly_fields = ('line_total',)
    autocomplete_fields = ['product']


@admin.register(Quote)
class QuoteAdmin(RBACModelAdminMixin, RestrictExportMixin, ModelAdmin):
    list_display = (
        'quote_number',
        'status_badge',
        'account',
        'contact',
        'total_display',
        'issue_date',
        'valid_until',
        'expired_badge'
    )
    list_filter = ('status', 'issue_date', 'valid_until')
    search_fields = ('quote_number', 'title', 'account__name', 'contact__first_name', 'contact__last_name')
    date_hierarchy = 'issue_date'
    list_select_related = ('account', 'contact', 'deal', 'created_by')
    inlines = [QuoteItemInline]
    autocomplete_fields = ['deal', 'account', 'contact']
    
    fieldsets = (
        ('Información General', {
            'fields': ('quote_number', 'title', 'description', 'status')
        }),
        ('Relaciones', {
            'fields': ('deal', 'account', 'contact', 'created_by')
        }),
        ('Términos Comerciales', {
            'fields': ('payment_terms', 'delivery_terms', 'notes')
        }),
        ('Totales', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_percent', 'discount_amount', 'total')
        }),
        ('Fechas', {
            'fields': ('issue_date', 'valid_until', 'sent_at', 'viewed_at', 'accepted_at')
        }),
    )
    readonly_fields = ('subtotal', 'tax_amount', 'discount_amount', 'total', 'sent_at', 'viewed_at', 'accepted_at')
    
    def status_badge(self, obj):
        colors = {
            'draft': '#64748b',
            'sent': '#0ea5e9',
            'viewed': '#8b5cf6',
            'accepted': '#10b981',
            'rejected': '#ef4444',
            'expired': '#6b7280',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;\">{}</span>',
            colors.get(obj.status, '#64748b'),
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Estado'
    
    def total_display(self, obj):
        return format_html('<strong>${:,.2f}</strong>', obj.total)
    total_display.short_description = 'Total'
    
    def expired_badge(self, obj):
        if obj.is_expired():
            return format_html(
                '<span style="background-color: #ef4444; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: 600;">⚠️ EXPIRADA</span>'
            )
        return '-'
    expired_badge.short_description = 'Estado'


@admin.register(QuoteItem)
class QuoteItemAdmin(ModelAdmin):
    list_display = ('quote', 'description', 'quantity', 'unit_price', 'discount_percent', 'line_total_display')
    list_filter = ('quote__status',)
    search_fields = ('description', 'quote__quote_number', 'product__name')
    autocomplete_fields = ['quote', 'product']
    
    def line_total_display(self, obj):
        return f"${obj.line_total:,.2f}"
    line_total_display.short_description = 'Total Línea'