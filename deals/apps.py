from django.apps import AppConfig


class DealsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deals'
    verbose_name = 'Gestión de Tratos'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import deals.signals
