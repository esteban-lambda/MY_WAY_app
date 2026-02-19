from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from .models import Contact
from deals.models import Deal
from interactions.models import Interaction

@login_required
def contacts_list(request):
    """Lista de todos los contactos con búsqueda"""
    query = request.GET.get('q', '')
    
    contacts = Contact.objects.select_related('account').annotate(
        deals_count=Count('deal'),
        interactions_count=Count('interaction')
    )
    
    if query:
        contacts = contacts.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(job_title__icontains=query) |
            Q(account__name__icontains=query)
        )
    
    contacts = contacts.order_by('first_name', 'last_name')
    
    context = {
        'contacts': contacts,
        'query': query,
    }
    return render(request, 'contacts/contacts_list.html', context)

@login_required
def contact_detail(request, contact_id):
    """Detalle de un contacto con sus deals e interacciones"""
    contact = get_object_or_404(Contact.objects.select_related('account'), id=contact_id)
    
    deals = Deal.objects.filter(contact=contact).select_related('account', 'assigned_to').order_by('-created_at')
    interactions = Interaction.objects.filter(contact=contact).select_related('assigned_to').order_by('-date')[:20]
    
    # Estadísticas del contacto
    total_deals = deals.count()
    won_deals = deals.filter(stage='closed_won').count()
    total_value = deals.aggregate(Sum('value'))['value__sum'] or 0
    
    context = {
        'contact': contact,
        'deals': deals,
        'interactions': interactions,
        'total_deals': total_deals,
        'won_deals': won_deals,
        'total_value': total_value,
    }
    return render(request, 'contacts/contact_detail.html', context)