from django.db import models
from django.contrib.auth.models import User
from model_utils import FieldTracker


class EmailTemplate(models.Model):
    """
    Plantillas reutilizables para emails
    """
    CATEGORY_CHOICES = [
        ('welcome', 'Bienvenida'),
        ('follow_up', 'Seguimiento'),
        ('proposal', 'Propuesta'),
        ('thank_you', 'Agradecimiento'),
        ('meeting', 'Reunión'),
        ('reminder', 'Recordatorio'),
        ('other', 'Otro'),
    ]
    
    name = models.CharField('Nombre', max_length=255)
    subject = models.CharField('Asunto', max_length=500)
    body_html = models.TextField('Cuerpo (HTML)')
    body_text = models.TextField('Cuerpo (Texto plano)', blank=True)
    category = models.CharField('Categoría', max_length=20, choices=CATEGORY_CHOICES, default='other')
    
    # Variables disponibles
    available_variables = models.TextField(
        'Variables disponibles',
        default='{{contact_name}}, {{contact_email}}, {{account_name}}, {{user_name}}',
        help_text='Variables que pueden ser usadas en el template'
    )
    
    is_active = models.BooleanField('Activa', default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField('Creada el', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizada el', auto_now=True)
    
    class Meta:
        verbose_name = 'Plantilla de Email'
        verbose_name_plural = 'Plantillas de Email'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class EmailLog(models.Model):
    """
    Registro de emails enviados
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('failed', 'Fallido'),
        ('opened', 'Abierto'),
        ('clicked', 'Click en enlace'),
    ]
    
    template = models.ForeignKey(
        EmailTemplate, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='logs'
    )
    to_email = models.EmailField('Para')
    from_email = models.EmailField('De')
    subject = models.CharField('Asunto', max_length=500)
    body_html = models.TextField('Cuerpo HTML', blank=True)
    body_text = models.TextField('Cuerpo texto', blank=True)
    
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField('Enviado el', null=True, blank=True)
    opened_at = models.DateTimeField('Abierto el', null=True, blank=True)
    clicked_at = models.DateTimeField('Click el', null=True, blank=True)
    
    # Relaciones
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey('accounts.Account', on_delete=models.SET_NULL, null=True, blank=True)
    contact = models.ForeignKey('contacts.Contact', on_delete=models.SET_NULL, null=True, blank=True)
    deal = models.ForeignKey('deals.Deal', on_delete=models.SET_NULL, null=True, blank=True)
    
    error_message = models.TextField('Mensaje de error', blank=True)
    created_at = models.DateTimeField('Creado el', auto_now_add=True)
    
    # Tracker para detectar cambios en campos
    tracker = FieldTracker(fields=['status'])
    
    class Meta:
        verbose_name = 'Log de Email'
        verbose_name_plural = 'Logs de Emails'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.to_email} ({self.get_status_display()})"
