from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os


def document_upload_path(instance, filename):
    """Determina la ruta de subida según el tipo de documento"""
    return f'documents/{instance.document_type}/{filename}'


class Document(models.Model):
    """
    Modelo para gestión de documentos
    """
    DOCUMENT_TYPE_CHOICES = [
        ('contract', 'Contrato'),
        ('proposal', 'Propuesta'),
        ('invoice', 'Factura'),
        ('quote', 'Cotización'),
        ('report', 'Reporte'),
        ('presentation', 'Presentación'),
        ('other', 'Otro'),
    ]
    
    name = models.CharField('Nombre', max_length=255)
    description = models.TextField('Descripción', blank=True)
    document_type = models.CharField('Tipo de documento', max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    
    file = models.FileField(
        'Archivo',
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv',
                                'jpg', 'jpeg', 'png']
        )]
    )
    file_size = models.IntegerField('Tamaño (bytes)', editable=False, null=True, blank=True)
    
    # Relaciones
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name='Cuenta'
    )
    contact = models.ForeignKey(
        'contacts.Contact',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name='Contacto'
    )
    deal = models.ForeignKey(
        'deals.Deal',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name='Trato'
    )
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Subido por')
    uploaded_at = models.DateTimeField('Subido el', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado el', auto_now=True)
    
    # Seguridad
    is_confidential = models.BooleanField('Confidencial', default=False)
    
    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_document_type_display()})"
    
    def save(self, *args, **kwargs):
        """Guarda el tamaño del archivo automáticamente"""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    def get_file_extension(self):
        """Retorna la extensión del archivo"""
        return os.path.splitext(self.file.name)[1].upper().replace('.', '')
    
    def get_file_size_display(self):
        """Retorna el tamaño del archivo en formato legible"""
        if not self.file_size:
            return '0 B'
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
