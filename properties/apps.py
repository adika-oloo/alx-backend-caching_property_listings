from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'
    
    def ready(self):
        """
        Import signals when the app is ready to register signal handlers
        """
        try:
            # Import signals module to register signal handlers
            import properties.signals
            logger.debug("Properties signals imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import properties signals: {e}")
        except Exception as e:
            logger.error(f"Error in properties signals: {e}")
