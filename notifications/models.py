from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    """
    Sistema de notificaciones para usuarios
    """
    TYPE_CHOICES = [
        ('task', 'Tarea'),
        ('deal', 'Trato'),
        ('interaction', 'Interacción'),
        ('mention', 'Mención'),
        ('reminder', 'Recordatorio'),
        ('system', 'Sistema'),
        ('other', 'Otro'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinatario'
    )
    notification_type = models.CharField(
        'Tipo',
        max_length=20,
        choices=TYPE_CHOICES,
        default='other'
    )
    priority = models.CharField(
        'Prioridad',
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    
    title = models.CharField('Título', max_length=255)
    message = models.TextField('Mensaje')
    action_url = models.CharField('URL de acción', max_length=500, blank=True)
    
    # Estado
    is_read = models.BooleanField('Leída', default=False)
    read_at = models.DateTimeField('Leída el', null=True, blank=True)
    
    # Relaciones opcionales
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, null=True, blank=True)
    deal = models.ForeignKey('deals.Deal', on_delete=models.CASCADE, null=True, blank=True)
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, null=True, blank=True)
    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField('Creada el', auto_now_add=True)
    expires_at = models.DateTimeField(
        'Expira el',
        null=True,
        blank=True,
        help_text='Fecha en que la notificación deja de ser relevante'
    )
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Marca la notificación como leída"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def is_expired(self):
        """Verifica si la notificación ha expirado"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
