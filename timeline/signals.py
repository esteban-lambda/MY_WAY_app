from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

from contacts.models import Contact
from accounts.models import Account
from deals.models import Deal, Quote
from interactions.models import Interaction
from tasks.models import Task
from documents.models import Document
from email_templates.models import EmailLog
from notifications.models import Notification


@receiver(post_save, sender=Contact)
def contact_saved(sender, instance, created, **kwargs):
    """Captura cuando se crea o actualiza un contacto"""
    from timeline.models import TimelineEvent
    
    action = 'created' if created else 'updated'
    title = f"Contacto {action}: {instance.first_name} {instance.last_name}"
    description = f"Email: {instance.email}, Teléfono: {instance.phone}"
    
    TimelineEvent.create_event(
        event_type='contact',
        action=action,
        title=title,
        description=description,
        content_object=instance,
        account=instance.account,
        contact=instance,
        metadata={
            'email': instance.email,
            'phone': instance.phone,
            'job_title': instance.job_title,
        }
    )


@receiver(post_save, sender=Account)
def account_saved(sender, instance, created, **kwargs):
    """Captura cuando se crea o actualiza una cuenta"""
    from timeline.models import TimelineEvent
    
    action = 'created' if created else 'updated'
    title = f"Cuenta {action}: {instance.name}"
    description = f"Industria: {instance.get_industry_display()}, Empleados: {instance.number_of_employees}"
    
    TimelineEvent.create_event(
        event_type='account',
        action=action,
        title=title,
        description=description,
        content_object=instance,
        account=instance,
        metadata={
            'industry': instance.industry,
            'revenue': str(instance.annual_revenue),
            'employees': instance.number_of_employees,
        }
    )


@receiver(post_save, sender=Deal)
def deal_saved(sender, instance, created, **kwargs):
    """Captura cuando se crea o actualiza un negocio"""
    from timeline.models import TimelineEvent
    
    action = 'created' if created else 'updated'
    
    # Detectar si cambió de stage
    if not created and instance.tracker.has_changed('stage'):
        action = 'moved'
        title = f"Negocio movido: {instance.name}"
        description = f"De {instance.tracker.previous('stage')} a {instance.stage}"
    elif instance.stage == 'closed_won':
        action = 'won'
        title = f"🎉 Negocio ganado: {instance.name}"
        description = f"Valor: ${instance.value:,.2f}"
    elif instance.stage == 'closed_lost':
        action = 'lost'
        title = f"Negocio perdido: {instance.name}"
        description = f"Valor: ${instance.value:,.2f}"
    else:
        title = f"Negocio {action}: {instance.name}"
        description = f"Etapa: {instance.stage}, Valor: ${instance.value:,.2f}"
    
    TimelineEvent.create_event(
        event_type='deal',
        action=action,
        title=title,
        description=description,
        content_object=instance,
        account=instance.account,
        contact=instance.contact,
        deal=instance,
        is_important=(action in ['won', 'lost']),
        metadata={
            'stage': instance.stage,
            'value': str(instance.value),
            'probability': str(instance.probability),
            'expected_close_date': instance.expected_close_date.isoformat() if instance.expected_close_date else None,
        }
    )


@receiver(post_save, sender=Interaction)
def interaction_saved(sender, instance, created, **kwargs):
    """Captura cuando se crea o actualiza una interacción"""
    from timeline.models import TimelineEvent
    
    if not created:
        return  # Solo registramos creaciones de interacciones
    
    title = f"{instance.get_interaction_type_display()}: {instance.subject}"
    description = instance.notes[:200] if instance.notes else ""
    
    # Determinar el tipo de evento según el tipo de interacción
    event_type_map = {
        'call': 'call',
        'email': 'email',
        'meeting': 'meeting',
        'note': 'note',
    }
    event_type = event_type_map.get(instance.interaction_type, 'interaction')
    
    TimelineEvent.create_event(
        event_type=event_type,
        action='created',
        title=title,
        description=description,
        user=instance.created_by,
        content_object=instance,
        account=instance.account,
        contact=instance.contact,
        deal=instance.deal,
        metadata={
            'interaction_type': instance.interaction_type,
            'duration': instance.duration,
            'date': instance.date.isoformat() if instance.date else None,
        }
    )


@receiver(post_save, sender=Task)
def task_saved(sender, instance, created, **kwargs):
    """Captura cuando se crea, actualiza o completa una tarea"""
    from timeline.models import TimelineEvent
    
    action = 'created' if created else 'updated'
    
    # Detectar si se completó
    if not created and instance.status == 'completed' and instance.tracker.has_changed('status'):
        action = 'completed'
        title = f"✅ Tarea completada: {instance.title}"
    else:
        title = f"Tarea {action}: {instance.title}"
    
    description = f"Prioridad: {instance.get_priority_display()}, Vencimiento: {instance.due_date.strftime('%d/%m/%Y') if instance.due_date else 'Sin fecha'}"
    
    TimelineEvent.create_event(
        event_type='task',
        action=action,
        title=title,
        description=description,
        user=instance.assigned_to,
        content_object=instance,
        account=instance.account,
        contact=instance.contact,
        deal=instance.deal,
        is_important=(action == 'completed' or instance.priority == 'urgent'),
        metadata={
            'priority': instance.priority,
            'status': instance.status,
            'type': instance.type,
            'due_date': instance.due_date.isoformat() if instance.due_date else None,
        }
    )


@receiver(post_save, sender=Document)
def document_saved(sender, instance, created, **kwargs):
    """Captura cuando se sube un documento"""
    from timeline.models import TimelineEvent
    
    if not created:
        return  # Solo registramos subidas de documentos
    
    title = f"📄 Documento subido: {instance.name}"
    description = f"Tipo: {instance.document_type}, Tamaño: {instance.get_file_size_display()}"
    
    TimelineEvent.create_event(
        event_type='document',
        action='uploaded',
        title=title,
        description=description,
        user=instance.uploaded_by,
        content_object=instance,
        account=instance.account,
        contact=instance.contact,
        deal=instance.deal,
        metadata={
            'document_type': instance.document_type,
            'file_size': instance.file_size,
            'is_confidential': instance.is_confidential,
        }
    )


@receiver(post_save, sender=EmailLog)
def email_log_saved(sender, instance, created, **kwargs):
    """Captura cuando se envía un email"""
    from timeline.models import TimelineEvent
    
    # Solo registramos emails enviados exitosamente
    if not created or instance.status != 'sent':
        # Si cambió a opened o clicked, actualizar
        if not created and instance.tracker.has_changed('status') and instance.status in ['opened', 'clicked']:
            action = instance.status
            title = f"📧 Email {action}: {instance.subject}"
            description = f"Para: {instance.to_email}"
            
            TimelineEvent.create_event(
                event_type='email',
                action=action,
                title=title,
                description=description,
                content_object=instance,
                account=instance.account,
                contact=instance.contact,
                deal=instance.deal,
                metadata={
                    'subject': instance.subject,
                    'recipient': instance.to_email,
                    'status': instance.status,
                }
            )
        return
    
    title = f"📧 Email enviado: {instance.subject}"
    description = f"Para: {instance.to_email}"
    
    TimelineEvent.create_event(
        event_type='email',
        action='sent',
        title=title,
        description=description,
        user=instance.sent_by,
        content_object=instance,
        account=instance.account,
        contact=instance.contact,
        deal=instance.deal,
        metadata={
            'subject': instance.subject,
            'recipient': instance.to_email,
            'template': instance.template.name if instance.template else None,
        }
    )


@receiver(post_save, sender=Quote)
def quote_saved(sender, instance, created, **kwargs):
    """Captura cuando se crea o cambia el estado de una cotización"""
    from timeline.models import TimelineEvent
    
    action = 'created' if created else 'updated'
    
    # Detectar cambios de estado significativos
    if not created and instance.tracker.has_changed('status'):
        if instance.status == 'accepted':
            action = 'accepted'
            title = f"💰 Cotización aceptada: {instance.quote_number}"
        elif instance.status == 'rejected':
            action = 'rejected'
            title = f"Cotización rechazada: {instance.quote_number}"
        elif instance.status == 'sent':
            action = 'sent'
            title = f"Cotización enviada: {instance.quote_number}"
        else:
            title = f"Cotización actualizada: {instance.quote_number}"
    else:
        title = f"Cotización {action}: {instance.quote_number}"
    
    description = f"Total: ${instance.total:,.2f}, Estado: {instance.get_status_display()}"
    
    TimelineEvent.create_event(
        event_type='quote',
        action=action,
        title=title,
        description=description,
        user=instance.created_by,
        content_object=instance,
        account=instance.account,
        contact=instance.contact,
        deal=instance.deal,
        is_important=(action in ['accepted', 'rejected']),
        metadata={
            'quote_number': instance.quote_number,
            'status': instance.status,
            'total': str(instance.total),
            'valid_until': instance.valid_until.isoformat() if instance.valid_until else None,
        }
    )


@receiver(post_save, sender=Notification)
def notification_saved(sender, instance, created, **kwargs):
    """Captura cuando se crea una notificación importante"""
    from timeline.models import TimelineEvent
    
    if not created or instance.notification_type == 'info':
        return  # Solo registramos notificaciones importantes nuevas
    
    title = f"🔔 {instance.title}"
    description = instance.message[:200]
    
    TimelineEvent.create_event(
        event_type='notification',
        action='created',
        title=title,
        description=description,
        user=instance.recipient,
        content_object=instance,
        is_important=(instance.priority in ['high', 'urgent']),
        metadata={
            'notification_type': instance.notification_type,
            'priority': instance.priority,
        }
    )
