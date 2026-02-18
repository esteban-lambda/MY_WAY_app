from django.shortcuts import render
from django.db.models import Sum, Count, F, DecimalField, Case, When
from django.db.models.functions import Coalesce
from deals.models import Deal

def dashboard_index(request):
    """Dashboard principal con estadísticas y forecasting"""
    
    # Deals activos (no cerrados perdidos)
    active_deals = Deal.objects.exclude(stage='closed_lost')
    
    # Estadísticas básicas
    total_revenue = Deal.objects.filter(stage='closed_won').aggregate(
        Sum('value'))['value__sum'] or 0
    total_deals = Deal.objects.count()
    active_deals_count = active_deals.count()
    
    # Win rate
    closed_deals = Deal.objects.filter(stage__in=['closed_won', 'closed_lost']).count()
    won_deals = Deal.objects.filter(stage='closed_won').count()
    win_rate = (won_deals / closed_deals * 100) if closed_deals > 0 else 0
    
    # FORECASTING: Valor nominal vs valor ponderado por etapa
    stage_stats = []
    total_nominal = 0
    total_weighted = 0
    
    for stage_key, stage_label in Deal.STAGES:
        if stage_key == 'closed_lost':
            continue  # No contamos deals perdidos en forecasting
            
        deals_in_stage = Deal.objects.filter(stage=stage_key)
        count = deals_in_stage.count()
        nominal_value = deals_in_stage.aggregate(Sum('value'))['value__sum'] or 0
        
        # Calcular valor ponderado
        probability = Deal.STAGE_PROBABILITIES.get(stage_key, 0)
        weighted_value = float(nominal_value) * probability
        
        total_nominal += float(nominal_value)
        total_weighted += weighted_value
        
        stage_stats.append({
            'stage': stage_key,
            'label': stage_label,
            'count': count,
            'nominal_value': nominal_value,
            'weighted_value': weighted_value,
            'probability': probability * 100,
        })
    
    # Datos para gráfica de funnel
    funnel_labels = [s['label'] for s in stage_stats]
    funnel_nominal = [float(s['nominal_value']) for s in stage_stats]
    funnel_weighted = [s['weighted_value'] for s in stage_stats]
    
    context = {
        'total_revenue': total_revenue,
        'total_deals': total_deals,
        'active_deals_count': active_deals_count,
        'win_rate': round(win_rate, 1),
        
        # Forecasting
        'total_nominal': total_nominal,
        'total_weighted': total_weighted,
        'forecast_confidence': (total_weighted / total_nominal * 100) if total_nominal > 0 else 0,
        'stage_stats': stage_stats,
        
        # Datos para gráficas
        'funnel_labels': funnel_labels,
        'funnel_nominal': funnel_nominal,
        'funnel_weighted': funnel_weighted,
    }
    return render(request, 'core/dashboard.html', context)

#  EL ERROR DE WEASYPRINT
# def export_dashboard_pdf(request):
#     pass