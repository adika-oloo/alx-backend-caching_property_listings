def getallproperties():
    """
    Fetch all Property records, using Redis low-level caching for 1 hour.
    """
    properties = cache.get("allproperties")
    if properties is None:
        # Query database if cache is empty
        properties = list(Property.objects.all().values(
            "id", "title", "description", "price_per_night",
            "bedrooms", "bathrooms", "guests",
            "country", "country_code", "category", "favorited", "created_at"
        ))
        # Cache for 1 hour
        cache.set("allproperties", properties, 3600)
    return properties


