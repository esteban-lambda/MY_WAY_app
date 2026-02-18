from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
            'hot': '#FAB95B',      # Accent (amarillo/dorado)
            'warm': '#547792',     # Secondary (azul grisáceo)
            'cold': '#1A3263',     # Primary (azul oscuro)
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
        return self.get_subtotal() * (self.discount_percent / 100)
    
    def get_total(self):
        """Calcula el total con descuento"""
        return self.get_subtotal() - self.get_discount_amount()