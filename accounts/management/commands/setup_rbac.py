"""
Sistema de Roles y Permisos (RBAC) para CRM
=============================================

Gestión de comando para crear grupos y asignar permisos
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Crea los grupos RBAC y asigna permisos para el CRM'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\\nConfigurando Sistema RBAC...\\n'))
        
        # Importar modelos
        from accounts.models import Account
        from contacts.models import Contact
        from deals.models import Deal, Product, DealProduct
        from interactions.models import Interaction
        
        # ===========================================
        # 1. SALES REPRESENTATIVE (Vendedor)
        # ==========================================
        sales_rep, created = Group.objects.get_or_create(name='Sales Representative')
        
        if created:
            self.stdout.write('  Creando grupo: Sales Representative')
        
        # Permisos de Sales Rep (solo CRUD en sus propios datos)
        sales_perms = []
        
        # Deals - Solo ver y editar sus propios deals
        deal_ct = ContentType.objects.get_for_model(Deal)
        sales_perms.extend([
            Permission.objects.get(codename='view_deal', content_type=deal_ct),
            Permission.objects.get(codename='add_deal', content_type=deal_ct),
            Permission.objects.get(codename='change_deal', content_type=deal_ct),
        ])
        
        # Contacts - Ver, agregar y editar
        contact_ct = ContentType.objects.get_for_model(Contact)
        sales_perms.extend([
            Permission.objects.get(codename='view_contact', content_type=contact_ct),
            Permission.objects.get(codename='add_contact', content_type=contact_ct),
            Permission.objects.get(codename='change_contact', content_type=contact_ct),
        ])
        
        # Accounts - Solo ver
        account_ct = ContentType.objects.get_for_model(Account)
        sales_perms.append(
            Permission.objects.get(codename='view_account', content_type=account_ct)
        )
        
        # Interactions - CRUD completo
        interaction_ct = ContentType.objects.get_for_model(Interaction)
        sales_perms.extend([
            Permission.objects.get(codename='view_interaction', content_type=interaction_ct),
            Permission.objects.get(codename='add_interaction', content_type=interaction_ct),
            Permission.objects.get(codename='change_interaction', content_type=interaction_ct),
            Permission.objects.get(codename='delete_interaction', content_type=interaction_ct),
        ])
        
        # Products - Solo ver
        product_ct = ContentType.objects.get_for_model(Product)
        sales_perms.append(
            Permission.objects.get(codename='view_product', content_type=product_ct)
        )
        
        # DealProduct - Agregar y modificar
        dealproduct_ct = ContentType.objects.get_for_model(DealProduct)
        sales_perms.extend([
            Permission.objects.get(codename='view_dealproduct', content_type=dealproduct_ct),
            Permission.objects.get(codename='add_dealproduct', content_type=dealproduct_ct),
            Permission.objects.get(codename='change_dealproduct', content_type=dealproduct_ct),
        ])
        
        sales_rep.permissions.set(sales_perms)
        self.stdout.write(self.style.SUCCESS(f'  Sales Representative: {len(sales_perms)} permisos asignados'))
        
        # ===========================================
        # 2. SALES MANAGER (Gerente de Ventas)
        # ===========================================
        sales_manager, created = Group.objects.get_or_create(name='Sales Manager')
        
        if created:
            self.stdout.write('  Creando grupo: Sales Manager')
        
        # Permisos de Sales Manager (todos los de Sales Rep + más acceso)
        manager_perms = list(sales_perms)  # Heredar permisos de Sales Rep
        
        # Deals - Acceso completo incluyendo eliminar
        manager_perms.append(
            Permission.objects.get(codename='delete_deal', content_type=deal_ct)
        )
        
        # Contacts - Acceso completo
        manager_perms.append(
            Permission.objects.get(codename='delete_contact', content_type=contact_ct)
        )
        
        # Accounts - Agregar y editar
        manager_perms.extend([
            Permission.objects.get(codename='add_account', content_type=account_ct),
            Permission.objects.get(codename='change_account', content_type=account_ct),
        ])
        
        # Products - Ver y modificar precios
        manager_perms.extend([
            Permission.objects.get(codename='add_product', content_type=product_ct),
            Permission.objects.get(codename='change_product', content_type=product_ct),
        ])
        
        # DealProduct - Acceso completo
        manager_perms.append(
            Permission.objects.get(codename='delete_dealproduct', content_type=dealproduct_ct)
        )
        
        sales_manager.permissions.set(manager_perms)
        self.stdout.write(self.style.SUCCESS(f'  Sales Manager: {len(manager_perms)} permisos asignados'))
        
        # ===========================================
        # 3. ADMINISTRATOR (Administrador)
        # ===========================================
        administrator, created = Group.objects.get_or_create(name='Administrator')
        
        if created:
            self.stdout.write('  Creando grupo: Administrator')
        
        # Administradores tienen TODOS los permisos
        admin_perms = Permission.objects.filter(
            content_type__in=[
                deal_ct, contact_ct, account_ct, 
                interaction_ct, product_ct, dealproduct_ct
            ]
        )
        
        administrator.permissions.set(admin_perms)
        self.stdout.write(self.style.SUCCESS(f'  Administrator: {admin_perms.count()} permisos asignados'))
        
        # Resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('\nSistema RBAC configurado exitosamente!\n'))
        self.stdout.write('Resumen de Grupos:')
        self.stdout.write(f'   Sales Representative: {sales_rep.permissions.count()} permisos')
        self.stdout.write(f'   Sales Manager: {sales_manager.permissions.count()} permisos')
        self.stdout.write(f'   Administrator: {administrator.permissions.count()} permisos')
        self.stdout.write('\nUso:')
        self.stdout.write('   - Asigna usuarios a grupos desde el Admin de Django')
        self.stdout.write('   - Los querysets se filtran automáticamente según el rol')
        self.stdout.write('\n')
