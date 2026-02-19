from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from model_utils import FieldTracker
from accounts.models import Account
from contacts.models import Contact


class Product(models.Model):
    """
    Catálogo de productos que se pueden vender
    """
    CATEGORY_CHOICES = [
        ('software', 'Software'),
        ('hardware', 'Hardware'),
        ('service', 'Servicio'),
        ('consulting', 'Consultoría'),
        ('subscription', 'Suscripción'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Nombre del producto')
    sku = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='SKU',
        help_text='Código único del producto'
    )
    description = models.TextField(blank=True, verbose_name='Descripción')
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES,
        verbose_name='Categoría'
    )
    unit_price = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        verbose_name='Precio unitario'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sku})"


class Deal(models.Model):
    STAGES = [
        ('prospecting', 'Prospección'),
        ('negotiation', 'Negociación'),
        ('closed_won', 'Cerrado Ganado'),
        ('closed_lost', 'Cerrado Perdido'),
    ]
    
    # Probabilidades de cierre por etapa (Forecasting)
    STAGE_PROBABILITIES = {
        'prospecting': 0.10,    # 10% de probabilidad
        'negotiation': 0.50,    # 50% de probabilidad
        'closed_won': 1.00,     # 100% (ya cerrado)
        'closed_lost': 0.00,    # 0% (perdido)
    }

    name = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='deals')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    stage = models.CharField(max_length=20, choices=STAGES, default='prospecting')
    expected_close_date = models.DateField(null=True, blank=True)
    
    # Nuevo campo para relacionar con productos
    products = models.ManyToManyField(
        Product, 
        through='DealProduct',
        related_name='deals',
        verbose_name='Productos'
    )
    
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_deals',
        verbose_name='Vendedor asignado'
    )
    
    # Lead Scoring System
    lead_score = models.IntegerField(
        default=0,
        verbose_name='Lead Score',
        help_text='Puntuación del lead (0-100) basada en Fit y Engagement'
    )
    last_score_update = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización de score'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    # Tracker para detectar cambios en campos
    tracker = FieldTracker(fields=['stage', 'value'])
    
    class Meta:
        verbose_name = 'Trato'
        verbose_name_plural = 'Tratos'
        ordering = ['-lead_score', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.value}"
    
    def get_score_category(self):
        """Retorna la categoría del lead según su puntuación"""
        if self.lead_score >= 80:
            return 'hot'  # Lead caliente
        elif self.lead_score >= 60:
            return 'warm'  # Lead tibio
        elif self.lead_score >= 40:
            return 'cold'  # Lead frío
        else:
            return 'frozen'  # Lead congelado
    
    def get_score_display_color(self):
        """Retorna el color HTML según la categoría del lead"""
        category = self.get_score_category()
        colors = {
            'hot': '#ef4444',      # Red-500 (caliente)
            'warm': '#0ea5e9',     # Sky-500 (templado)
            'cold': '#64748b',     # Slate-500 (frío)
            'frozen': '#999999'    # Gris
        }
        return colors.get(category, '#999999')
    
    def calculate_total_from_products(self):
        """Calcula el valor total basado en los productos agregados"""
        total = sum(
            item.quantity * item.unit_price 
            for item in self.deal_products.all()
        )
        return total
    
    def get_probability(self):
        """Retorna la probabilidad de cierre según la etapa actual"""
        return self.STAGE_PROBABILITIES.get(self.stage, 0.0)
    
    @property
    def weighted_value(self):
        """Valor ponderado del deal según probabilidad de cierre (Forecasting)"""
        return float(self.value) * self.get_probability()
    
    @property
    def weighted_value_display(self):
        """Valor ponderado formateado para mostrar"""
        return f"${self.weighted_value:,.2f}"


class DealProduct(models.Model):
    """
    Tabla intermedia para relacionar Deals con Products
    Permite especificar cantidad, precio y descuento por producto
    """
    deal = models.ForeignKey(
        Deal, 
        on_delete=models.CASCADE,
        related_name='deal_products',
        verbose_name='Trato'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name='Producto'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    unit_price = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        verbose_name='Precio unitario',
        help_text='Precio al momento del deal (puede diferir del precio actual)'
    )
    discount_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        verbose_name='Descuento (%)'
    )
    
    class Meta:
        verbose_name = 'Producto del Trato'
        verbose_name_plural = 'Productos del Trato'
        unique_together = ('deal', 'product')
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} en {self.deal.name}"
    
    def get_subtotal(self):
        """Calcula el subtotal sin descuento"""
        return self.quantity * self.unit_price
    
    def get_discount_amount(self):
        """Calcula el monto del descuento"""
        return self.get_subtotal() * (self.discount_percent / Decimal('100'))
    
    def get_total(self):
        """Calcula el total con descuento"""
        return self.get_subtotal() - self.get_discount_amount()


class Quote(models.Model):
    """
    Sistema de cotizaciones
    """
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('sent', 'Enviada'),
        ('viewed', 'Vista'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
        ('expired', 'Expirada'),
    ]
    
    quote_number = models.CharField('Número de cotización', max_length=50, unique=True)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='quotes', verbose_name='Trato')
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, verbose_name='Empresa')
    contact = models.ForeignKey('contacts.Contact', on_delete=models.SET_NULL, null=True, verbose_name='Contacto')
    
    title = models.CharField('Título', max_length=255)
    description = models.TextField('Descripción', blank=True)
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # Términos comerciales
    payment_terms = models.TextField(
        'Términos de pago',
        default='Pago en 30 días',
        help_text='Condiciones de pago'
    )
    delivery_terms = models.TextField(
        'Términos de entrega',
        blank=True,
        help_text='Condiciones de entrega'
    )
    notes = models.TextField('Notas adicionales', blank=True)
    
    # Impuestos y descuentos
    subtotal = models.DecimalField('Subtotal', max_digits=15, decimal_places=2, default=0)
    tax_rate = models.DecimalField('Tasa de impuesto (%)', max_digits=5, decimal_places=2, default=21.00)
    tax_amount = models.DecimalField('Monto de impuestos', max_digits=15, decimal_places=2, default=0)
    discount_percent = models.DecimalField('Descuento (%)', max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField('Monto de descuento', max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=15, decimal_places=2, default=0)
    
    # Fechas
    issue_date = models.DateField('Fecha de emisión')
    valid_until = models.DateField('Válida hasta')
    created_at = models.DateTimeField('Creada el', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizada el', auto_now=True)
    sent_at = models.DateTimeField('Enviada el', null=True, blank=True)
    viewed_at = models.DateTimeField('Vista el', null=True, blank=True)
    accepted_at = models.DateTimeField('Aceptada el', null=True, blank=True)
    
    # Usuario responsable
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='quotes_created',
        verbose_name='Creada por'
    )
    
    # Tracker para detectar cambios en campos
    tracker = FieldTracker(fields=['status'])
    
    class Meta:
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['account']),
            models.Index(fields=['deal']),
        ]
    
    def __str__(self):
        return f"{self.quote_number} - {self.account.name}"
    
    def calculate_totals(self):
        """Calcula los totales de la cotización"""
        items = self.items.all()
        self.subtotal = sum([item.get_line_total() for item in items])
        
        # Calcular descuento
        if self.discount_percent > 0:
            self.discount_amount = (self.subtotal * self.discount_percent) / 100
        
        # Calcular impuestos
        subtotal_after_discount = self.subtotal - self.discount_amount
        self.tax_amount = (subtotal_after_discount * self.tax_rate) / 100
        
        # Total final
        self.total = subtotal_after_discount + self.tax_amount
        self.save()
    
    def mark_sent(self):
        """Marca la cotización como enviada"""
        from django.utils import timezone
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_accepted(self):
        """Marca la cotización como aceptada"""
        from django.utils import timezone
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.save()
    
    def is_expired(self):
        """Verifica si la cotización ha expirado"""
        from datetime import date
        return date.today() > self.valid_until and self.status not in ['accepted', 'rejected']
    
    def get_status_color(self):
        """Retorna color según estado"""
        colors = {
            'draft': '#64748b',      # Slate-500
            'sent': '#0ea5e9',       # Sky-500
            'viewed': '#8b5cf6',     # Purple-500
            'accepted': '#10b981',   # Green-500
            'rejected': '#ef4444',   # Red-500
            'expired': '#6b7280',    # Gray-500
        }
        return colors.get(self.status, '#64748b')


class QuoteItem(models.Model):
    """
    Items de una cotización
    """
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items', verbose_name='Cotización')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Producto')
    
    description = models.CharField('Descripción', max_length=500)
    quantity = models.IntegerField('Cantidad', default=1)
    unit_price = models.DecimalField('Precio unitario', max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField('Descuento (%)', max_digits=5, decimal_places=2, default=0)
    line_total = models.DecimalField('Total línea', max_digits=10, decimal_places=2, default=0)
    
    order = models.IntegerField('Orden', default=0)
    created_at = models.DateTimeField('Creado el', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item de Cotización'
        verbose_name_plural = 'Items de Cotización'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.unit_price}"
    
    def get_line_total(self):
        """Calcula el total de la línea"""
        subtotal = self.quantity * self.unit_price
        if self.discount_percent > 0:
            discount = (subtotal * self.discount_percent) / 100
            return subtotal - discount
        return subtotal
    
    def save(self, *args, **kwargs):
        self.line_total = self.get_line_total()
        super().save(*args, **kwargs)
        # Recalcular totales de la cotización
        self.quote.calculate_totals()