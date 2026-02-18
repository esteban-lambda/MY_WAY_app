"""
Mixins para control de acceso basado en roles (RBAC)
====================================================

Proporciona querysets filtrados según el rol del usuario
"""

from django.contrib import admin
from django.db.models import Q


class RBACModelAdminMixin:
    """
    Mixin para ModelAdmin que filtra querysets según el rol del usuario:
    
    - Sales Representative: Solo ve sus propios registros
    - Sales Manager: Ve todo su equipo
    - Administrator: Ve todo
    """
    
    def get_queryset(self, request):
        """
        Filtra el queryset según el rol del usuario
        """
        qs = super().get_queryset(request)
        
        # Superusuarios ven todo
        if request.user.is_superuser:
            return qs
        
        # Verificar si el usuario tiene perfil y determinar rol
        if hasattr(request.user, 'profile'):
            role = request.user.profile.role
            
            # Administrator: Ve todo
            if role == 'manager' or request.user.groups.filter(name='Administrator').exists():
                return qs
            
            # Sales Manager: Ve su equipo
            if request.user.groups.filter(name='Sales Manager').exists():
                return self._filter_for_sales_manager(qs, request.user)
            
            # Sales Representative: Solo sus registros
            if role == 'sales' or request.user.groups.filter(name='Sales Representative').exists():
                return self._filter_for_sales_rep(qs, request.user)
        
        # Por defecto, si tiene grupo Administrator
        if request.user.groups.filter(name='Administrator').exists():
            return qs
        
        # Sales Manager
        if request.user.groups.filter(name='Sales Manager').exists():
            return self._filter_for_sales_manager(qs, request.user)
        
        # Sales Representative por defecto
        return self._filter_for_sales_rep(qs, request.user)
    
    def _filter_for_sales_rep(self, qs, user):
        """
        Filtro para Sales Representative:
        Solo registros donde él es el assigned_to o created_by
        """
        model_name = qs.model.__name__
        
        # Para Deal: Solo deals asignados a él
        if model_name == 'Deal':
            return qs.filter(assigned_to=user)
        
        # Para Interaction: Solo interacciones asignadas o creadas por él
        if model_name == 'Interaction':
            return qs.filter(Q(assigned_to=user) | Q(created_by=user))
        
        # Para Contact: Solo contactos de empresas con deals del vendedor
        if model_name == 'Contact':
            from deals.models import Deal
            # Obtener accounts de los deals del vendedor
            account_ids = Deal.objects.filter(
                assigned_to=user
            ).values_list('account_id', flat=True).distinct()
            return qs.filter(account_id__in=account_ids)
        
        # Para Account: Solo empresas con deals del vendedor
        if model_name == 'Account':
            from deals.models import Deal
            account_ids = Deal.objects.filter(
                assigned_to=user
            ).values_list('account_id', flat=True).distinct()
            return qs.filter(id__in=account_ids)
        
        # Para Product y DealProduct: Ver todos
        if model_name in ['Product', 'DealProduct']:
            return qs
        
        return qs
    
    def _filter_for_sales_manager(self, qs, user):
        """
        Filtro para Sales Manager:
        Ve todo su equipo (Sales Reps que él creó) + sus propios registros
        """
        model_name = qs.model.__name__
        
        # Obtener vendedores de su equipo
        from accounts.models import UserProfile
        team_users = UserProfile.objects.filter(
            created_by=user
        ).values_list('user_id', flat=True)
        
        # Incluir al manager mismo
        all_users = list(team_users) + [user.id]
        
        # Para Deal: Deals de su equipo
        if model_name == 'Deal':
            return qs.filter(assigned_to_id__in=all_users)
        
        # Para Interaction: Interacciones de su equipo
        if model_name == 'Interaction':
            return qs.filter(
                Q(assigned_to_id__in=all_users) | Q(created_by_id__in=all_users)
            )
        
        # Para Contact: Contactos relacionados con deals de su equipo
        if model_name == 'Contact':
            from deals.models import Deal
            account_ids = Deal.objects.filter(
                assigned_to_id__in=all_users
            ).values_list('account_id', flat=True).distinct()
            return qs.filter(account_id__in=account_ids)
        
        # Para Account: Empresas con deals de su equipo
        if model_name == 'Account':
            from deals.models import Deal
            account_ids = Deal.objects.filter(
                assigned_to_id__in=all_users
            ).values_list('account_id', flat=True).distinct()
            return qs.filter(id__in=account_ids)
        
        # Para Product y DealProduct: Ver todos
        return qs
    
    def has_change_permission(self, request, obj=None):
        """
        Controla permisos de edición
        """
        # Superusuarios y administradores pueden todo
        if request.user.is_superuser or request.user.groups.filter(name='Administrator').exists():
            return True
        
        # Si no hay objeto, retornar True (para la vista de lista)
        if obj is None:
            return True
        
        # Sales Representative: Solo puede editar sus propios registros
        if request.user.groups.filter(name='Sales Representative').exists():
            # Para Deal
            if hasattr(obj, 'assigned_to'):
                return obj.assigned_to == request.user
            # Para Interaction
            if hasattr(obj, 'created_by'):
                return obj.created_by == request.user or obj.assigned_to == request.user
        
        # Sales Manager: Puede editar registros de su equipo
        if request.user.groups.filter(name='Sales Manager').exists():
            from accounts.models import UserProfile
            team_users = UserProfile.objects.filter(
                created_by=request.user
            ).values_list('user_id', flat=True)
            
            if hasattr(obj, 'assigned_to'):
                return obj.assigned_to_id in team_users or obj.assigned_to == request.user
        
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """
        Controla permisos de eliminación
        Sales Rep NO puede eliminar
        """
        # Superusuarios y administradores pueden todo
        if request.user.is_superuser or request.user.groups.filter(name='Administrator').exists():
            return True
        
        # Sales Representative: NO puede eliminar
        if request.user.groups.filter(name='Sales Representative').exists():
            return False
        
        # Sales Manager: Puede eliminar registros de su equipo
        if request.user.groups.filter(name='Sales Manager').exists():
            if obj is None:
                return True
            
            from accounts.models import UserProfile
            team_users = UserProfile.objects.filter(
                created_by=request.user
            ).values_list('user_id', flat=True)
            
            if hasattr(obj, 'assigned_to'):
                return obj.assigned_to_id in team_users or obj.assigned_to == request.user
        
        return super().has_delete_permission(request, obj)


class RestrictExportMixin:
    """
    Mixin para restringir exportación de datos
    Solo Administrators pueden exportar
    """
    
    def has_export_permission(self, request):
        """Solo administradores pueden exportar"""
        return (
            request.user.is_superuser or 
            request.user.groups.filter(name='Administrator').exists()
        )
    
    def changelist_view(self, request, extra_context=None):
        """Ocultar botones de exportación para no-administradores"""
        extra_context = extra_context or {}
        
        # Verificar si puede exportar
        can_export = self.has_export_permission(request)
        extra_context['can_export'] = can_export
        
        return super().changelist_view(request, extra_context=extra_context)
