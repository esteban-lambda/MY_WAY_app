from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from model_utils import FieldTracker
from accounts.models import Account
from contacts.models import Contact
from deals.models import Deal


class Task(models.Model):
    """
    Modelo para gestión de tareas
    """
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    TYPE_CHOICES = [
        ('call', 'Llamar'),
        ('email', 'Enviar Email'),
        ('meeting', 'Reunión'),
        ('follow_up', 'Seguimiento'),
        ('research', 'Investigación'),
        ('proposal', 'Preparar Propuesta'),
        ('other', 'Otro'),
    ]
    
    title = models.CharField('Título', max_length=255)
    description = models.TextField('Descripción', blank=True)
    task_type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES, default='other')
    priority = models.CharField('Prioridad', max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField('Estado', max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Relaciones
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tasks_assigned',
        verbose_name='Asignado a'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='tasks_created',
        verbose_name='Creado por'
    )
    account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='tasks',
        verbose_name='Empresa'
    )
    contact = models.ForeignKey(
        Contact, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='tasks',
        verbose_name='Contacto'
    )
    deal = models.ForeignKey(
        Deal, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='tasks',
        verbose_name='Trato'
    )
    
    # Fechas
    due_date = models.DateTimeField('Fecha límite')
    completed_at = models.DateTimeField('Completada el', null=True, blank=True)
    created_at = models.DateTimeField('Creada el', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizada el', auto_now=True)
    
    # Recordatorio
    reminder_minutes = models.IntegerField(
        'Recordatorio (minutos antes)', 
        default=30,
        help_text='Minutos antes de la fecha límite para enviar recordatorio'
    )
    reminder_sent = models.BooleanField('Recordatorio enviado', default=False)
    
    # Tracker para detectar cambios en campos
    tracker = FieldTracker(fields=['status'])
    
    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['-due_date', '-priority']
        indexes = [
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def is_overdue(self):
        """Verifica si la tarea está vencida"""
        return self.status != 'completed' and self.due_date < timezone.now()
    
    def mark_completed(self):
        """Marca la tarea como completada"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def get_priority_color(self):
        """Retorna color según prioridad"""
        colors = {
            'low': '#64748b',       # Slate-500
            'medium': '#0ea5e9',    # Sky-500
            'high': '#f97316',      # Orange-500
            'urgent': '#ef4444',    # Red-500
        }
        return colors.get(self.priority, '#64748b')


class TaskComment(models.Model):
    """
    Comentarios en tareas para comunicación del equipo
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField('Comentario')
    created_at = models.DateTimeField('Creado el', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Comentario de Tarea'
        verbose_name_plural = 'Comentarios de Tareas'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comentario de {self.user.username} en {self.task.title}"

