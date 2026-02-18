from django.db import models

class TimeStampedModel(models.Model):
    """
    Clase abstracta para que todos nuestros modelos 
    tengan fecha de creación y actualización automáticamente.
    """
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última modificación", auto_now=True)

    class Meta:
        abstract = True