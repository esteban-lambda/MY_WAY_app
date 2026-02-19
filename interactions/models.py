from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from accounts.models import Account
from contacts.models import Contact
from deals.models import Deal


class Interaction(models.Model):
    """
    Modelo base para interacciones (llamadas, reuniones, emails, notas)
    """
    INTERACTION_TYPE_CHOICES = [
        ('call', 'Llamada'),
        ('meeting', 'Reunión'),
        ('email', 'Email'),
        ('note', 'Nota'),
    ]
    
    DIRECTION_CHOICES = [
        ('inbound', 'Entrante'),
        ('outbound', 'Saliente'),
        ('internal', 'Interno'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Programada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    interaction_type = models.CharField(
        max_length=20, 
        choices=INTERACTION_TYPE_CHOICES,
        verbose_name='Tipo'
    )
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        default='outbound',
        verbose_name='Dirección'
    )
    subject = models.CharField(max_length=255, verbose_name='Asunto')
    summary = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Resumen ejecutivo',
        help_text='Resumen breve de la interacción'
    )
    description = models.TextField(blank=True, verbose_name='Descripción detallada')
    
    # Relaciones
    account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='interactions',
        verbose_name='Empresa'
    )
    contact = models.ForeignKey(
        Contact, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='interactions',
        verbose_name='Contacto'
    )
    deal = models.ForeignKey(
        Deal, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='interactions',
        verbose_name='Trato relacionado'
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='interactions',
        verbose_name='Asignado a'
    )
    
    # Detalles de tiempo
    scheduled_at = models.DateTimeField(verbose_name='Fecha programada')
    duration_minutes = models.PositiveIntegerField(
        default=30, 
        verbose_name='Duración (minutos)'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='scheduled',
        verbose_name='Estado'
    )
    
    # Notas y resultados
    notes = models.TextField(blank=True, verbose_name='Notas')
    outcome = models.TextField(blank=True, verbose_name='Resultado')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_interactions'
    )
    
    class Meta:
        ordering = ['-scheduled_at']
        verbose_name = 'Interacción'
        verbose_name_plural = 'Interacciones'
        indexes = [
            models.Index(fields=['-scheduled_at']),
            models.Index(fields=['contact', '-scheduled_at']),
            models.Index(fields=['deal', '-scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.get_interaction_type_display()} - {self.subject} ({self.account})"
    
    @staticmethod
    def calculate_next_contact_date(contact=None, deal=None):
        """
        Calcula la próxima fecha de contacto sugerida basada en la frecuencia
        de las últimas interacciones del contacto o deal.
        
        Lógica:
        - Analiza las últimas 5 interacciones
        - Calcula el promedio de días entre interacciones
        - Sugiere la próxima fecha basada en ese promedio
        - Si no hay suficiente historial, sugiere 7 días por defecto
        """
        now = timezone.now()
        
        # Construir queryset según lo que se pase
        qs = Interaction.objects.filter(
            status='completed',
            scheduled_at__lte=now
        )
        
        if contact:
            qs = qs.filter(contact=contact)
        elif deal:
            qs = qs.filter(deal=deal)
        else:
            return now + timedelta(days=7)  # Default
        
        # Obtener últimas interacciones
        recent_interactions = list(
            qs.order_by('-scheduled_at')[:5].values_list('scheduled_at', flat=True)
        )
        
        if len(recent_interactions) < 2:
            # No hay suficiente historial, sugerir 7 días
            return now + timedelta(days=7)
        
        # Calcular intervalos entre interacciones
        intervals = []
        for i in range(len(recent_interactions) - 1):
            delta = (recent_interactions[i] - recent_interactions[i + 1]).days
            intervals.append(delta)
        
        # Promedio de días entre interacciones
        avg_interval = sum(intervals) / len(intervals)
        
        # Ajustes inteligentes
        if avg_interval < 3:
            suggested_days = 3  # Mínimo 3 días
        elif avg_interval > 30:
            suggested_days = 30  # Máximo 30 días
        else:
            suggested_days = int(avg_interval)
        
        # Calcular próxima fecha desde la última interacción
        last_interaction_date = recent_interactions[0]
        next_date = last_interaction_date + timedelta(days=suggested_days)
        
        # Si la fecha calculada ya pasó, usar hoy + intervalo
        if next_date < now:
            next_date = now + timedelta(days=suggested_days)
        
        return next_date
    
    def get_next_suggested_contact(self):
        """Método de instancia para obtener la próxima fecha sugerida"""
        return self.calculate_next_contact_date(
            contact=self.contact,
            deal=self.deal
        )


class Call(models.Model):
    """
    Modelo específico para llamadas telefónicas
    """
    CALL_DIRECTION_CHOICES = [
        ('inbound', 'Entrante'),
        ('outbound', 'Saliente'),
    ]
    
    CALL_OUTCOME_CHOICES = [
        ('connected', 'Conectado'),
        ('no_answer', 'Sin respuesta'),
        ('voicemail', 'Buzón de voz'),
        ('busy', 'Ocupado'),
    ]
    
    interaction = models.OneToOneField(
        Interaction, 
        on_delete=models.CASCADE, 
        related_name='call_details'
    )
    phone_number = models.CharField(max_length=20, verbose_name='Número de teléfono')
    direction = models.CharField(
        max_length=10, 
        choices=CALL_DIRECTION_CHOICES,
        verbose_name='Dirección'
    )
    call_outcome = models.CharField(
        max_length=20, 
        choices=CALL_OUTCOME_CHOICES,
        blank=True,
        verbose_name='Resultado de llamada'
    )
    
    class Meta:
        verbose_name = 'Llamada'
        verbose_name_plural = 'Llamadas'
    
    def __str__(self):
        return f"Llamada {self.get_direction_display()} - {self.phone_number}"


class Meeting(models.Model):
    """
    Modelo específico para reuniones
    """
    MEETING_TYPE_CHOICES = [
        ('in_person', 'Presencial'),
        ('video', 'Videollamada'),
        ('phone', 'Telefónica'),
    ]
    
    interaction = models.OneToOneField(
        Interaction, 
        on_delete=models.CASCADE, 
        related_name='meeting_details'
    )
    meeting_type = models.CharField(
        max_length=20, 
        choices=MEETING_TYPE_CHOICES,
        verbose_name='Tipo de reunión'
    )
    location = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name='Ubicación / Link'
    )
    attendees = models.ManyToManyField(
        Contact, 
        blank=True,
        related_name='meetings_attended',
        verbose_name='Asistentes'
    )
    
    class Meta:
        verbose_name = 'Reunión'
        verbose_name_plural = 'Reuniones'
    
    def __str__(self):
        return f"Reunión {self.get_meeting_type_display()} - {self.interaction.subject}"
