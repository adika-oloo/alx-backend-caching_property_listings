from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from .models import Property

@cache_page(60 * 15)  # Cache the response for 15 minutes
def property_list(request):
    properties = Property.objects.all().values(
        "id", "title", "description", "price_per_night",
        "bedrooms", "bathrooms", "guests",
        "country", "country_code", "category", "favorited", "created_at"
    )
    return JsonResponse(list(properties), safe=False)

