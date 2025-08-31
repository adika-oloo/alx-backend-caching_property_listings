from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'
    
    def ready(self):
        """
        Import signals when the app is ready
        """
        try:
            # Import signals module to register signal handlers
            from . import signals
            logger.debug("Properties signals imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import properties signals: {e}")
