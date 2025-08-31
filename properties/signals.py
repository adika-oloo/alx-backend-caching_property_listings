from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Property)
def clear_properties_cache_on_save(sender, instance, **kwargs):
    """
    Clear the properties cache when a Property is saved
    """
    try:
        cache.delete('all_properties')
        logger.debug(f"Properties cache cleared after save of Property {instance.id}")
    except Exception as e:
        logger.error(f"Error clearing cache on save: {e}")

@receiver(post_delete, sender=Property)
def clear_properties_cache_on_delete(sender, instance, **kwargs):
    """
    Clear the properties cache when a Property is deleted
    """
    try:
        cache.delete('all_properties')
        logger.debug(f"Properties cache cleared after delete of Property {instance.id}")
    except Exception as e:
        logger.error(f"Error clearing cache on delete: {e}")

# Additional signal handlers for related models if needed
@receiver(post_save)
@receiver(post_delete)
def clear_cache_on_related_changes(sender, **kwargs):
    """
    Clear cache when related models change (optional)
    You can add specific logic here for models that affect properties
    """
    # Add logic to determine if this model affects properties
    # For example, if you have Booking model that references Property
    # you might want to clear cache when bookings change
    pass
