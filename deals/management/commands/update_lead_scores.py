"""
Comando para recalcular el Lead Score de todos los Deals
Uso: python manage.py update_lead_scores
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from deals.models import Deal
from deals.signals import calculate_lead_score


class Command(BaseCommand):
    help = 'Recalcula el Lead Score de todos los deals existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada de cada deal',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        
        self.stdout.write(self.style.WARNING('Iniciando recálculo de Lead Scores...'))
        self.stdout.write('')
        
        deals = Deal.objects.all()
        total_deals = deals.count()
        
        if total_deals == 0:
            self.stdout.write(self.style.WARNING('No hay deals en la base de datos'))
            return
        
        updated_count = 0
        hot_leads = 0
        warm_leads = 0
        cold_leads = 0
        frozen_leads = 0
        
        for deal in deals:
            old_score = deal.lead_score
            new_score = calculate_lead_score(deal)
            
            # Actualizar el deal
            Deal.objects.filter(pk=deal.pk).update(
                lead_score=new_score,
                last_score_update=timezone.now()
            )
            
            # Contar por categoría
            if new_score >= 80:
                hot_leads += 1
            elif new_score >= 60:
                warm_leads += 1
            elif new_score >= 40:
                cold_leads += 1
            else:
                frozen_leads += 1
            
            updated_count += 1
            
            if verbose:
                change_indicator = '+' if new_score > old_score else ('-' if new_score < old_score else '=')
                self.stdout.write(
                    f'  {change_indicator} {deal.name}: {old_score} → {new_score}'
                )
        
        # Resumen final
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'{updated_count} deals actualizados'))
        self.stdout.write('')
        self.stdout.write('Distribución de Leads:')
        self.stdout.write(f'   Hot Leads (80-100):    {hot_leads}')
        self.stdout.write(f'   Warm Leads (60-79):    {warm_leads}')
        self.stdout.write(f'   Cold Leads (40-59):    {cold_leads}')
        self.stdout.write(f'   Frozen Leads (0-39):   {frozen_leads}')
        self.stdout.write('')
        
        # Mostrar top 5 hot leads
        top_leads = Deal.objects.order_by('-lead_score')[:5]
        if top_leads:
            self.stdout.write(self.style.SUCCESS('Top 5 Hot Leads:'))
            for i, deal in enumerate(top_leads, 1):
                self.stdout.write(
                    f'   {i}. {deal.name} - Score: {deal.lead_score} ({deal.account})'
                )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Proceso completado!'))
