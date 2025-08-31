from django.core.cache import cache
from .models import Property

def getallproperties():
    # Try to get cached queryset
    properties = cache.get("allproperties")
    if properties is None:
        # Fetch from database if not cached
        properties = list(Property.objects.all().values(
            "id", "title", "description", "price_per_night",
            "bedrooms", "bathrooms", "guests",
            "country", "country_code", "category", "favorited", "created_at"
        ))
        # Store in Redis for 1 hour
        cache.set("allproperties", properties, 3600)
    return properties

