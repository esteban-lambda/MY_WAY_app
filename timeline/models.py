from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

class TimelineEvent(models.Model):
    """
    Modelo para registrar eventos cronológicos en el CRM.
    Utiliza GenericForeignKey para vincular cualquier tipo de objeto.
    """
    
    # Tipos de eventos
    EVENT_TYPE_CHOICES = [
        ('interaction', 'Interacción'),
        ('task', 'Tarea'),
        ('deal', 'Negocio'),
        ('contact', 'Contacto'),
        ('account', 'Cuenta'),
        ('document', 'Documento'),
        ('email', 'Email'),
        ('notification', 'Notificación'),
        ('quote', 'Cotización'),
        ('note', 'Nota'),
        ('call', 'Llamada'),
        ('meeting', 'Reunión'),
        ('system', 'Sistema'),
    ]
    
    # Acciones
    ACTION_CHOICES = [
        ('created', 'Creado'),
        ('updated', 'Actualizado'),
        ('deleted', 'Eliminado'),
        ('completed', 'Completado'),
        ('sent', 'Enviado'),
        ('received', 'Recibido'),
        ('opened', 'Abierto'),
        ('clicked', 'Clic realizado'),
        ('assigned', 'Asignado'),
        ('moved', 'Movido'),
        ('won', 'Ganado'),
        ('lost', 'Perdido'),
        ('accepted', 'Aceptado'),
        ('rejected', 'Rechazado'),
        ('uploaded', 'Subido'),
        ('downloaded', 'Descargado'),
        ('called', 'Llamado'),
        ('met', 'Reunido'),
    ]
    
    # Información del evento
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, db_index=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Usuario que realizó la acción
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='timeline_events')
    
    # Relación genérica con cualquier modelo
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)  # Para datos adicionales estructurados
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Relaciones opcionales para filtrado rápido
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, null=True, blank=True, related_name='timeline_events')
    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, null=True, blank=True, related_name='timeline_events')
    deal = models.ForeignKey('deals.Deal', on_delete=models.CASCADE, null=True, blank=True, related_name='timeline_events')
    
    # Visibilidad
    is_public = models.BooleanField(default=True)  # Si es visible para todos o solo para el usuario
    is_important = models.BooleanField(default=False)  # Para destacar eventos importantes
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['account', '-created_at']),
            models.Index(fields=['contact', '-created_at']),
            models.Index(fields=['deal', '-created_at']),
        ]
        verbose_name = 'Evento de Timeline'
        verbose_name_plural = 'Eventos de Timeline'
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.title} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"
    
    def get_icon(self):
        """Retorna el icono apropiado según el tipo de evento"""
        icons = {
            'interaction': '💬',
            'task': '✅',
            'deal': '💼',
            'contact': '👤',
            'account': '🏢',
            'document': '📄',
            'email': '📧',
            'notification': '🔔',
            'quote': '💰',
            'note': '📝',
            'call': '📞',
            'meeting': '🤝',
            'system': '⚙️',
        }
        return icons.get(self.event_type, '📌')
    
    def get_color(self):
        """Retorna el color apropiado según el tipo de evento"""
        colors = {
            'interaction': '#0ea5e9',
            'task': '#10b981',
            'deal': '#3b82f6',
            'contact': '#8b5cf6',
            'account': '#6366f1',
            'document': '#f59e0b',
            'email': '#ec4899',
            'notification': '#ef4444',
            'quote': '#14b8a6',
            'note': '#64748b',
            'call': '#06b6d4',
            'meeting': '#8b5cf6',
            'system': '#6b7280',
        }
        return colors.get(self.event_type, '#64748b')
    
    @staticmethod
    def create_event(event_type, action, title, description='', user=None, 
                     content_object=None, metadata=None, account=None, 
                     contact=None, deal=None, is_important=False):
        """
        Método helper para crear eventos fácilmente
        """
        event = TimelineEvent(
            event_type=event_type,
            action=action,
            title=title,
            description=description,
            user=user,
            metadata=metadata or {},
            account=account,
            contact=contact,
            deal=deal,
            is_important=is_important,
        )
        
        if content_object:
            event.content_object = content_object
        
        event.save()
        return event
