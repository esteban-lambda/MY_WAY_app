from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .serializers import (
    UserSerializer, AccountSerializer, ContactSerializer,
    DealSerializer, ProductSerializer, InteractionSerializer,
    TaskSerializer, TaskCommentSerializer, DocumentSerializer,
    EmailTemplateSerializer, EmailLogSerializer, NotificationSerializer
)
from accounts.models import Account
from contacts.models import Contact
from deals.models import Deal, Product
from interactions.models import Interaction
from tasks.models import Task, TaskComment
from documents.models import Document
from email_templates.models import EmailTemplate, EmailLog
from notifications.models import Notification
from django.contrib.auth.models import User


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint para usuarios"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']


class AccountViewSet(viewsets.ModelViewSet):
    """API endpoint para empresas"""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['industry']
    search_fields = ['name', 'industry', 'website']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']


class ContactViewSet(viewsets.ModelViewSet):
    """API endpoint para contactos"""
    queryset = Contact.objects.select_related('account')
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account']
    search_fields = ['first_name', 'last_name', 'email', 'job_title']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    ordering = ['first_name']


class DealViewSet(viewsets.ModelViewSet):
    """API endpoint para tratos"""
    queryset = Deal.objects.select_related('account', 'contact', 'assigned_to')
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stage', 'account', 'assigned_to']
    search_fields = ['name', 'account__name']
    ordering_fields = ['name', 'value', 'close_date', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def by_stage(self, request):
        """Agrupa deals por etapa"""
        stages = Deal.STAGES
        result = {}
        for stage_code, stage_name in stages:
            deals = self.queryset.filter(stage=stage_code)
            result[stage_code] = {
                'name': stage_name,
                'count': deals.count(),
                'total_value': sum([deal.value for deal in deals]),
                'deals': DealSerializer(deals, many=True).data
            }
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def forecast(self, request):
        """Retorna el forecast de ventas"""
        deals = self.queryset.exclude(stage__in=['closed_won', 'closed_lost'])
        forecast = {
            'total_deals': deals.count(),
            'total_value': sum([deal.value for deal in deals]),
            'weighted_value': sum([deal.weighted_value for deal in deals]),
            'by_stage': {}
        }
        
        for stage_code, stage_name in Deal.STAGES:
            stage_deals = deals.filter(stage=stage_code)
            if stage_deals.exists():
                forecast['by_stage'][stage_code] = {
                    'name': stage_name,
                    'count': stage_deals.count(),
                    'total_value': sum([deal.value for deal in stage_deals]),
                    'weighted_value': sum([deal.weighted_value for deal in stage_deals]),
                }
        
        return Response(forecast)


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoint para productos"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'sku', 'category', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']


class InteractionViewSet(viewsets.ModelViewSet):
    """API endpoint para interacciones"""
    queryset = Interaction.objects.select_related('account', 'contact', 'deal', 'assigned_to')
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['interaction_type', 'direction', 'status', 'account', 'contact', 'assigned_to']
    search_fields = ['subject', 'summary', 'description']
    ordering_fields = ['scheduled_at', 'created_at']
    ordering = ['-scheduled_at']
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Retorna interacciones próximas (siguiente semana)"""
        from datetime import timedelta
        now = timezone.now()
        next_week = now + timedelta(days=7)
        interactions = self.queryset.filter(
            scheduled_at__gte=now,
            scheduled_at__lte=next_week,
            status='scheduled'
        )
        serializer = self.get_serializer(interactions, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """API endpoint para tareas"""
    queryset = Task.objects.select_related('assigned_to', 'created_by', 'account', 'contact', 'deal')
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'task_type', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'created_at']
    ordering = ['-due_date']
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marca la tarea como completada"""
        task = self.get_object()
        task.mark_completed()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Retorna tareas vencidas"""
        tasks = self.queryset.filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Retorna tareas del usuario actual"""
        tasks = self.queryset.filter(assigned_to=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class DocumentViewSet(viewsets.ModelViewSet):
    """API endpoint para documentos"""
    queryset = Document.objects.select_related('uploaded_by', 'account', 'contact', 'deal')
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'account', 'contact', 'deal', 'is_confidential']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """API endpoint para plantillas de email"""
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'subject', 'body_html']


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint para logs de emails (solo lectura)"""
    queryset = EmailLog.objects.select_related('template', 'sent_by', 'account', 'contact', 'deal')
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'sent_by', 'account', 'contact']
    search_fields = ['subject', 'to_email']
    ordering_fields = ['sent_at', 'created_at']
    ordering = ['-created_at']


class NotificationViewSet(viewsets.ModelViewSet):
    """API endpoint para notificaciones"""
    queryset = Notification.objects.select_related('recipient', 'task', 'deal', 'account', 'contact')
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'priority', 'is_read', 'recipient']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Retorna notificaciones no leídas del usuario actual"""
        notifications = self.queryset.filter(recipient=request.user, is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marca una notificación como leída"""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Marca todas las notificaciones del usuario como leídas"""
        notifications = self.queryset.filter(recipient=request.user, is_read=False)
        for notification in notifications:
            notification.mark_as_read()
        return Response({'status': 'success', 'count': notifications.count()})
