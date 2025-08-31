from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from .utils import getallproperties  # import the new function

@cache_page(60 * 15)
def property_list(request):
    properties = getallproperties()  # use the low-level cached function
    return JsonResponse({"data": properties})





