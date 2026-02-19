from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Interaction

@login_required
def interactions_list(request):
    """Lista de todas las interacciones con filtros"""
    interaction_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    query = request.GET.get('q', '')
    
    interactions = Interaction.objects.select_related('account', 'contact', 'assigned_to')
    
    if interaction_type:
        interactions = interactions.filter(interaction_type=interaction_type)
    
    if status:
        interactions = interactions.filter(status=status)
    
    if query:
        interactions = interactions.filter(
            Q(subject__icontains=query) |
            Q(account__name__icontains=query) |
            Q(contact__first_name__icontains=query) |
            Q(contact__last_name__icontains=query)
        )
    
    interactions = interactions.order_by('-scheduled_at')
    
    # Estadísticas rápidas
    total_count = interactions.count()
    calls_count = interactions.filter(interaction_type='call').count()
    meetings_count = interactions.filter(interaction_type='meeting').count()
    completed_count = interactions.filter(status='completed').count()
    
    context = {
        'interactions': interactions[:100],  # Limitar a 100 para performance
        'interaction_type': interaction_type,
        'status': status,
        'query': query,
        'total_count': total_count,
        'calls_count': calls_count,
        'meetings_count': meetings_count,
        'completed_count': completed_count,
    }
    return render(request, 'interactions/interactions_list.html', context)

@login_required
def interaction_detail(request, interaction_id):
    """Detalle de una interacción"""
    interaction = get_object_or_404(
        Interaction.objects.select_related('account', 'contact', 'assigned_to'),
        id=interaction_id
    )
    
    context = {
        'interaction': interaction,
    }
    return render(request, 'interactions/interaction_detail.html', context)
