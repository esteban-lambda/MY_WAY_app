from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .models import TimelineEvent


@login_required
def timeline_view(request):
    """Vista principal del timeline unificado"""
    
    # Filtros
    event_type = request.GET.get('type', '')
    account_id = request.GET.get('account', '')
    contact_id = request.GET.get('contact', '')
    deal_id = request.GET.get('deal', '')
    user_id = request.GET.get('user', '')
    important_only = request.GET.get('important', '')
    
    # Query base
    events = TimelineEvent.objects.select_related(
        'user', 'account', 'contact', 'deal', 'content_type'
    ).all()
    
    # Aplicar filtros
    if event_type:
        events = events.filter(event_type=event_type)
    
    if account_id:
        events = events.filter(account_id=account_id)
    
    if contact_id:
        events = events.filter(contact_id=contact_id)
    
    if deal_id:
        events = events.filter(deal_id=deal_id)
    
    if user_id:
        events = events.filter(user_id=user_id)
    
    if important_only:
        events = events.filter(is_important=True)
    
    # Buscar
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(events, 50)  # 50 eventos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contexto para filtros
    from accounts.models import Account
    from contacts.models import Contact
    from deals.models import Deal
    from django.contrib.auth.models import User
    
    context = {
        'page_obj': page_obj,
        'event_types': TimelineEvent.EVENT_TYPE_CHOICES,
        'accounts': Account.objects.all()[:100],
        'contacts': Contact.objects.all()[:100],
        'deals': Deal.objects.all()[:100],
        'users': User.objects.filter(is_active=True),
        'filters': {
            'type': event_type,
            'account': account_id,
            'contact': contact_id,
            'deal': deal_id,
            'user': user_id,
            'important': important_only,
            'search': search_query,
        }
    }
    
    return render(request, 'timeline/timeline.html', context)


@login_required
def timeline_account(request, account_id):
    """Timeline de una cuenta específica"""
    from accounts.models import Account
    
    account = Account.objects.get(id=account_id)
    events = TimelineEvent.objects.filter(
        account=account
    ).select_related('user', 'contact', 'deal', 'content_type')
    
    # Paginación
    paginator = Paginator(events, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'account': account,
        'title': f'Timeline - {account.name}'
    }
    
    return render(request, 'timeline/timeline_detail.html', context)


@login_required
def timeline_contact(request, contact_id):
    """Timeline de un contacto específico"""
    from contacts.models import Contact
    
    contact = Contact.objects.get(id=contact_id)
    events = TimelineEvent.objects.filter(
        contact=contact
    ).select_related('user', 'account', 'deal', 'content_type')
    
    # Paginación
    paginator = Paginator(events, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'contact': contact,
        'title': f'Timeline - {contact.first_name} {contact.last_name}'
    }
    
    return render(request, 'timeline/timeline_detail.html', context)


@login_required
def timeline_deal(request, deal_id):
    """Timeline de un negocio específico"""
    from deals.models import Deal
    
    deal = Deal.objects.get(id=deal_id)
    events = TimelineEvent.objects.filter(
        deal=deal
    ).select_related('user', 'account', 'contact', 'content_type')
    
    # Paginación
    paginator = Paginator(events, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'deal': deal,
        'title': f'Timeline - {deal.name}'
    }
    
    return render(request, 'timeline/timeline_detail.html', context)
