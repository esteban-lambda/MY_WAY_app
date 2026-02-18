from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel 

class Account(models.Model):
    name = models.CharField("Nombre de la empresa", max_length=255)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    # Metadata básica
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Extensión del modelo User para añadir roles y permisos personalizados
    """
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('sales', 'Vendedor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_users'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"
    
    def is_manager(self):
        return self.role == 'manager'
    
    def is_sales(self):
        return self.role == 'sales'
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'