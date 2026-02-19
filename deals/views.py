from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Deal

@login_required
def pipeline_view(request):
    deals = Deal.objects.select_related('account').all()
    # orden de las columnas
    stages = [
        ('prospecting', 'Prospección'),
        ('negotiation', 'Negociación'),
        ('closed_won', 'Ganado'),
        ('closed_lost', 'Perdido'),
    ]
    return render(request, 'deals/pipeline.html', {'deals': deals, 'stages': stages})

def update_deal_stage(request, deal_id):
    if request.method == "POST":
        new_stage = request.POST.get('stage')
        deal = get_object_or_404(Deal, id=deal_id) 
        deal.stage = new_stage
        deal.save()
        return HttpResponse(f"Estado actualizado a {new_stage}")
    return HttpResponse(status=405)