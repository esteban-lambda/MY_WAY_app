from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, AccountViewSet, ContactViewSet,
    DealViewSet, ProductViewSet, InteractionViewSet,
    TaskViewSet, DocumentViewSet, EmailTemplateViewSet,
    EmailLogViewSet, NotificationViewSet
)

# Crear router y registrar viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'deals', DealViewSet, basename='deal')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'interactions', InteractionViewSet, basename='interaction')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'email-templates', EmailTemplateViewSet, basename='emailtemplate')
router.register(r'email-logs', EmailLogViewSet, basename='emaillog')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
