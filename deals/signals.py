"""
Sistema de Lead Scoring Sobrio B2B
====================================

Metodología de dos ejes:
1. FIT (50%): Qué tan bien encaja la empresa (datos estáticos)
2. ENGAGEMENT (50%): Nivel de interés mostrado (datos dinámicos)

Score final: 0-100 puntos
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from deals.models import Deal, DealProduct
from interactions.models import Interaction


def calculate_fit_score(deal):
    """
    Eje A: Perfil de Empresa (FIT) - 50 puntos máximo
    Evalúa qué tan bien encaja el cliente con nuestro perfil ideal
    """
    score = 0
    
    # 1. Industria Objetivo (20 puntos)
    target_industries = ['Software', 'Technology', 'Consulting', 'SaaS']
    if deal.account and deal.account.industry:
        if deal.account.industry in target_industries:
            score += 20
        elif deal.account.industry:  # Cualquier otra industria
            score += 10
    
    # 2. Tamaño del Deal / Budget (15 puntos)
    if deal.value:
        if deal.value >= 50000:
            score += 15  # High-value deal
        elif deal.value >= 20000:
            score += 10  # Medium-value deal
        elif deal.value >= 5000:
            score += 5   # Low-value deal
    
    # 3. Cargo del Contacto (15 puntos)
    if deal.contact and deal.contact.job_title:
        job_title_lower = deal.contact.job_title.lower()
        executive_titles = ['ceo', 'cto', 'cfo', 'director', 'vp', 'president', 'founder']
        manager_titles = ['manager', 'jefe', 'head', 'lead']
        
        if any(title in job_title_lower for title in executive_titles):
            score += 15  # C-Level o Director
        elif any(title in job_title_lower for title in manager_titles):
            score += 10  # Manager level
        else:
            score += 5   # Otro contacto
    
    return min(score, 50)  # Cap at 50 points


def calculate_engagement_score(deal):
    """
    Eje B: Actividad (ENGAGEMENT) - 50 puntos máximo
    Evalúa el nivel de interés e interacción del lead
    """
    score = 0
    now = timezone.now()
    
    # 1. Recencia de Interacciones (25 puntos)
    last_interaction = Interaction.objects.filter(
        deal=deal
    ).order_by('-scheduled_at').first()
    
    if last_interaction:
        days_since_interaction = (now - last_interaction.scheduled_at).days
        
        if days_since_interaction <= 3:
            score += 25  # Muy reciente (últimos 3 días)
        elif days_since_interaction <= 7:
            score += 20  # Reciente (última semana)
        elif days_since_interaction <= 14:
            score += 15  # Menos de 2 semanas
        elif days_since_interaction <= 30:
            score += 10  # Último mes
        elif days_since_interaction <= 60:
            score += 5   # Últimos 2 meses
        # Si no hay interacción en 60+ días, no suma puntos
    
    # 2. Frecuencia de Interacciones (10 puntos)
    # Contar interacciones en los últimos 30 días
    recent_interactions_count = Interaction.objects.filter(
        deal=deal,
        scheduled_at__gte=now - timedelta(days=30)
    ).count()
    
    if recent_interactions_count >= 5:
        score += 10  # Muy activo
    elif recent_interactions_count >= 3:
        score += 7   # Activo
    elif recent_interactions_count >= 1:
        score += 4   # Algo de actividad
    
    # 3. Velocidad del Pipeline (15 puntos)
    # Penalizar si el deal está estancado
    if deal.created_at:
        days_in_stage = (now - deal.created_at).days
        
        # Benchmark: Deals deberían moverse cada 14-30 días en promedio
        if deal.stage == 'prospecting':
            if days_in_stage <= 14:
                score += 15  # En tiempo
            elif days_in_stage <= 30:
                score += 10  # Aceptable
            elif days_in_stage <= 60:
                score += 5   # Lento
            # Más de 60 días en prospecting: sin puntos
                
        elif deal.stage == 'negotiation':
            if days_in_stage <= 30:
                score += 15  # En tiempo
            elif days_in_stage <= 60:
                score += 10  # Aceptable
            elif days_in_stage <= 90:
                score += 5   # Lento
    
    return min(score, 50)  # Cap at 50 points


def calculate_degradation(deal):
    """
    Degradación por Inactividad
    Resta 5 puntos por cada semana sin interacciones
    """
    penalty = 0
    now = timezone.now()
    
    last_interaction = Interaction.objects.filter(
        deal=deal
    ).order_by('-scheduled_at').first()
    
    if last_interaction:
        days_inactive = (now - last_interaction.scheduled_at).days
        weeks_inactive = days_inactive // 7
        
        # Penalización: 5 puntos por semana de inactividad (máximo -30 puntos)
        if weeks_inactive > 0:
            penalty = min(weeks_inactive * 5, 30)
    
    elif deal.created_at:
        # Si nunca ha habido interacciones, penalizar desde la creación del deal
        days_inactive = (now - deal.created_at).days
        weeks_inactive = days_inactive // 7
        
        if weeks_inactive > 2:  # Dar gracia de 2 semanas
            penalty = min((weeks_inactive - 2) * 5, 30)
    
    return penalty


def calculate_lead_score(deal):
    """
    Cálculo principal del Lead Score
    Combina Fit + Engagement - Degradación
    """
    fit_score = calculate_fit_score(deal)
    engagement_score = calculate_engagement_score(deal)
    degradation = calculate_degradation(deal)
    
    # Score final (0-100)
    total_score = fit_score + engagement_score - degradation
    
    # Asegurar que esté en el rango válido
    final_score = max(0, min(total_score, 100))
    
    return final_score


@receiver(post_save, sender=Deal)
def update_deal_score_on_save(sender, instance, created, **kwargs):
    """
    Recalcula el score cada vez que se guarda un Deal
    Nota: Usamos update() para evitar loop infinito
    """
    # Evitar loop infinito: solo recalcular si el score no se acaba de actualizar
    if not hasattr(instance, '_skip_score_update'):
        new_score = calculate_lead_score(instance)
        
        # Actualizar sin disparar signal nuevamente
        Deal.objects.filter(pk=instance.pk).update(
            lead_score=new_score,
            last_score_update=timezone.now()
        )


@receiver(post_save, sender=Interaction)
def update_deal_score_on_interaction(sender, instance, **kwargs):
    """
    Recalcula el score del deal cuando se crea/actualiza una interacción
    """
    if instance.deal:
        new_score = calculate_lead_score(instance.deal)
        
        Deal.objects.filter(pk=instance.deal.pk).update(
            lead_score=new_score,
            last_score_update=timezone.now()
        )


@receiver(post_delete, sender=Interaction)
def update_deal_score_on_interaction_delete(sender, instance, **kwargs):
    """
    Recalcula el score del deal cuando se elimina una interacción
    """
    if instance.deal:
        new_score = calculate_lead_score(instance.deal)
        
        Deal.objects.filter(pk=instance.deal.pk).update(
            lead_score=new_score,
            last_score_update=timezone.now()
        )


@receiver(post_save, sender=DealProduct)
@receiver(post_delete, sender=DealProduct)
def update_deal_on_product_change(sender, instance, **kwargs):
    """
    Actualiza automáticamente el valor del Deal y recalcula el score
    cuando se agregan, modifican o eliminan productos
    
    Esta es una funcionalidad crítica para mantener la integridad
    contable del sistema.
    """
    if instance.deal:
        # 1. Calcular el nuevo valor total desde los productos
        total_value = instance.deal.calculate_total_from_products()
        
        # 2. Recalcular el lead score (que usa el valor)
        new_score = calculate_lead_score(instance.deal)
        
        # 3. Actualizar ambos campos en una sola operación
        Deal.objects.filter(pk=instance.deal.pk).update(
            value=total_value,
            lead_score=new_score,
            last_score_update=timezone.now()
        )

