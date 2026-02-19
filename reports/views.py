from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from accounts.models import Account
from contacts.models import Contact
from deals.models import Deal, DealProduct
from interactions.models import Interaction
from tasks.models import Task
from email_templates.models import EmailLog
from timeline.models import TimelineEvent


@login_required
def reports_dashboard(request):
    """Dashboard principal de reportes"""
    # Período de análisis
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_90_days = today - timedelta(days=90)
    
    # KPIs principales
    total_deals = Deal.objects.count()
    total_accounts = Account.objects.count()
    total_contacts = Contact.objects.count()
    
    # Pipeline value
    pipeline_value = Deal.objects.exclude(
        stage__in=['closed_won', 'closed_lost']
    ).aggregate(total=Sum('value'))['total'] or 0
    
    # Won vs Lost (últimos 30 días)
    won_deals = Deal.objects.filter(
        stage='closed_won',
        updated_at__gte=last_30_days
    ).aggregate(
        count=Count('id'),
        value=Sum('value')
    )
    
    lost_deals = Deal.objects.filter(
        stage='closed_lost',
        updated_at__gte=last_30_days
    ).aggregate(
        count=Count('id'),
        value=Sum('value')
    )
    
    # Win rate
    total_closed = (won_deals['count'] or 0) + (lost_deals['count'] or 0)
    win_rate = (won_deals['count'] or 0) / total_closed * 100 if total_closed > 0 else 0
    
    # Tareas pendientes vs completadas
    tasks_stats = {
        'pending': Task.objects.filter(status__in=['pending', 'in_progress']).count(),
        'completed': Task.objects.filter(status='completed').count(),
        'overdue': Task.objects.filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        ).count()
    }
    
    # Interacciones por tipo (últimos 30 días)
    interactions_by_type = Interaction.objects.filter(
        date__gte=last_30_days
    ).values('interaction_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Deals por etapa
    deals_by_stage = Deal.objects.values('stage').annotate(
        count=Count('id'),
        total_value=Sum('value')
    ).order_by('-total_value')
    
    # Top 5 cuentas por valor
    top_accounts = Account.objects.annotate(
        total_value=Sum('deals__value')
    ).filter(total_value__isnull=False).order_by('-total_value')[:5]
    
    # Actividad reciente
    recent_activity = TimelineEvent.objects.select_related(
        'user', 'account', 'contact', 'deal'
    ).filter(is_important=True)[:10]
    
    context = {
        'today': today,
        'kpis': {
            'total_deals': total_deals,
            'total_accounts': total_accounts,
            'total_contacts': total_contacts,
            'pipeline_value': pipeline_value,
            'win_rate': round(win_rate, 1),
        },
        'won_deals': won_deals,
        'lost_deals': lost_deals,
        'tasks_stats': tasks_stats,
        'interactions_by_type': interactions_by_type,
        'deals_by_stage': deals_by_stage,
        'top_accounts': top_accounts,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'reports/dashboard.html', context)


@login_required
def sales_report(request):
    """Reporte de ventas"""
    # Período
    period = request.GET.get('period', '30')  # days
    today = timezone.now().date()
    start_date = today - timedelta(days=int(period))
    
    # Ventas ganadas
    won_deals = Deal.objects.filter(
        stage='closed_won',
        updated_at__gte=start_date
    ).select_related('account', 'assigned_to')
    
    # Totales
    total_won = won_deals.aggregate(
        count=Count('id'),
        total_value=Sum('value'),
        avg_value=Avg('value')
    )
    
    # Por mes
    monthly_sales = won_deals.annotate(
        month=TruncMonth('updated_at')
    ).values('month').annotate(
        count=Count('id'),
        total=Sum('value')
    ).order_by('month')
    
    # Por vendedor
    sales_by_user = won_deals.values(
        'assigned_to__first_name', 'assigned_to__last_name'
    ).annotate(
        count=Count('id'),
        total_value=Sum('value')
    ).order_by('-total_value')[:10]
    
    # Por producto
    product_sales = DealProduct.objects.filter(
        deal__stage='closed_won',
        deal__updated_at__gte=start_date
    ).values('product__name').annotate(
        count=Sum('quantity'),
        total_value=Sum(F('quantity') * F('unit_price'))
    ).order_by('-total_value')[:10]
    
    context = {
        'period': period,
        'start_date': start_date,
        'total_won': total_won,
        'won_deals': won_deals,
        'monthly_sales': monthly_sales,
        'sales_by_user': sales_by_user,
        'product_sales': product_sales,
    }
    
    return render(request, 'reports/sales.html', context)


@login_required
def pipeline_report(request):
    """Reporte de pipeline"""
    # Deals activos (no cerrados)
    active_deals = Deal.objects.exclude(
        stage__in=['closed_won', 'closed_lost']
    ).select_related('account', 'assigned_to')
    
    # Pipeline por etapa
    pipeline_by_stage = active_deals.values('stage').annotate(
        count=Count('id'),
        total_value=Sum('value'),
        weighted_value=Sum(F('value') * F('probability') / 100)
    ).order_by('stage')
    
    # Pipeline por vendedor
    pipeline_by_user = active_deals.values(
        'assigned_to__first_name', 'assigned_to__last_name'
    ).annotate(
        count=Count('id'),
        total_value=Sum('value'),
        weighted_value=Sum(F('value') * F('probability') / 100)
    ).order_by('-weighted_value')
    
    # Forecast (próximos 30, 60, 90 días)
    today = timezone.now().date()
    forecast_30 = active_deals.filter(
        expected_close_date__lte=today + timedelta(days=30)
    ).aggregate(
        count=Count('id'),
        total=Sum('value'),
        weighted=Sum(F('value') * F('probability') / 100)
    )
    
    forecast_60 = active_deals.filter(
        expected_close_date__lte=today + timedelta(days=60)
    ).aggregate(
        count=Count('id'),
        total=Sum('value'),
        weighted=Sum(F('value') * F('probability') / 100)
    )
    
    forecast_90 = active_deals.filter(
        expected_close_date__lte=today + timedelta(days=90)
    ).aggregate(
        count=Count('id'),
        total=Sum('value'),
        weighted=Sum(F('value') * F('probability') / 100)
    )
    
    # Deals aging (tiempo en pipeline)
    deals_with_age = []
    for deal in active_deals:
        if deal.created_at:
            days_in_pipeline = (timezone.now() - deal.created_at).days
            deals_with_age.append({
                'deal': deal,
                'days': days_in_pipeline
            })
    deals_with_age.sort(key=lambda x: x['days'], reverse=True)
    
    context = {
        'active_deals': active_deals,
        'pipeline_by_stage': pipeline_by_stage,
        'pipeline_by_user': pipeline_by_user,
        'forecast_30': forecast_30,
        'forecast_60': forecast_60,
        'forecast_90': forecast_90,
        'deals_with_age': deals_with_age[:20],  # Top 20 más antiguos
    }
    
    return render(request, 'reports/pipeline.html', context)


@login_required
def activity_report(request):
    """Reporte de actividad"""
    # Período
    period = request.GET.get('period', '30')
    today = timezone.now().date()
    start_date = today - timedelta(days=int(period))
    
    # Interacciones
    interactions = Interaction.objects.filter(
        date__gte=start_date
    )
    
    interactions_by_type = interactions.values('interaction_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    interactions_by_user = interactions.values(
        'created_by__first_name', 'created_by__last_name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Interacciones por día
    daily_interactions = interactions.annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Emails
    emails = EmailLog.objects.filter(
        sent_at__gte=start_date
    )
    
    email_stats = {
        'sent': emails.filter(status='sent').count(),
        'opened': emails.filter(status='opened').count(),
        'clicked': emails.filter(status='clicked').count(),
        'failed': emails.filter(status='failed').count(),
    }
    
    # Open rate
    total_sent = email_stats['sent']
    email_stats['open_rate'] = (email_stats['opened'] / total_sent * 100) if total_sent > 0 else 0
    email_stats['click_rate'] = (email_stats['clicked'] / total_sent * 100) if total_sent > 0 else 0
    
    # Tareas
    tasks = Task.objects.filter(
        created_at__gte=start_date
    )
    
    tasks_by_status = tasks.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    tasks_by_user = tasks.values(
        'assigned_to__first_name', 'assigned_to__last_name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Timeline events
    timeline_events = TimelineEvent.objects.filter(
        created_at__gte=start_date
    )
    
    events_by_type = timeline_events.values('event_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'period': period,
        'start_date': start_date,
        'interactions_by_type': interactions_by_type,
        'interactions_by_user': interactions_by_user,
        'daily_interactions': daily_interactions,
        'email_stats': email_stats,
        'tasks_by_status': tasks_by_status,
        'tasks_by_user': tasks_by_user,
        'events_by_type': events_by_type,
    }
    
    return render(request, 'reports/activity.html', context)


@login_required
def accounts_report(request):
    """Reporte de cuentas"""
    # Todas las cuentas con estadísticas
    accounts = Account.objects.annotate(
        deals_count=Count('deals'),
        deals_value=Sum('deals__value'),
        contacts_count=Count('contacts', distinct=True),
        interactions_count=Count('interactions', distinct=True),
        tasks_count=Count('tasks', distinct=True),
        documents_count=Count('documents', distinct=True),
    ).order_by('-deals_value')
    
    # Por industria
    by_industry = accounts.values('industry').annotate(
        count=Count('id'),
        total_value=Sum('deals__value')
    ).order_by('-count')
    
    # Por tamaño (empleados)
    size_ranges = [
        ('1-10', 1, 10),
        ('11-50', 11, 50),
        ('51-200', 51, 200),
        ('201-500', 201, 500),
        ('500+', 501, 999999),
    ]
    
    by_size = []
    for label, min_emp, max_emp in size_ranges:
        count = accounts.filter(
            number_of_employees__gte=min_emp,
            number_of_employees__lte=max_emp
        ).count()
        by_size.append({'label': label, 'count': count})
    
    # Top cuentas por valor
    top_accounts = accounts.filter(
        deals_value__isnull=False
    )[:20]
    
    # Cuentas sin actividad reciente (últimos 60 días)
    inactive_threshold = timezone.now() - timedelta(days=60)
    inactive_accounts = accounts.filter(
        Q(interactions__date__lt=inactive_threshold) | Q(interactions__isnull=True)
    ).distinct()[:20]
    
    context = {
        'accounts': accounts,
        'by_industry': by_industry,
        'by_size': by_size,
        'top_accounts': top_accounts,
        'inactive_accounts': inactive_accounts,
    }
    
    return render(request, 'reports/accounts.html', context)
