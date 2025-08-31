from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from .utils import getallproperties  # note the function name

@cache_page(60 * 15)
def property_list(request):
    properties = getallproperties()  # call the corrected function
    return JsonResponse({"data": properties})




