import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import logging
from .models import Property

logger = logging.getLogger(__name__)

def get_all_properties():
    """
    Get all properties with caching mechanism
    Cache results for 1 hour (3600 seconds) to improve performance
    """
    cached_properties = cache.get('all_properties')
    
    if cached_properties is not None:
        logger.debug("Returning cached properties")
        return cached_properties
    
    logger.debug("Fetching properties from database")
    properties = Property.objects.all().order_by('-created_at')
    
    # Cache the queryset for 1 hour
    cache.set('all_properties', properties, 3600)
    
    return properties

def get_country_code(country_name):
    """
    Get country code from country name using REST Countries API
    """
    cache_key = f'country_code_{country_name.lower()}'
    cached_code = cache.get(cache_key)
    
    if cached_code:
        return cached_code
    
    try:
        response = requests.get(
            f'https://restcountries.com/v3.1/name/{country_name}',
            timeout=5
        )
        response.raise_for_status()
        
        data = response.json()
        if data and isinstance(data, list):
            country_code = data[0].get('cca2', '').upper()
            # Cache for 24 hours
            cache.set(cache_key, country_code, 60 * 60 * 24)
            return country_code
            
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch country code for {country_name}: {e}")
    
    return None

def validate_property_data(data):
    """
    Validate property data before saving
    """
    errors = {}
    
    # Validate price
    if 'price_per_night' in data and data['price_per_night'] <= 0:
        errors['price_per_night'] = 'Price must be greater than 0'
    
    # Validate numeric fields
    numeric_fields = ['bedrooms', 'bathrooms', 'guests']
    for field in numeric_fields:
        if field in data and data[field] < 0:
            errors[field] = f'{field.capitalize()} cannot be negative'
    
    # Validate category
    if 'category' in data:
        valid_categories = dict(Property.PROPERTY_CATEGORIES).keys()
        if data['category'] not in valid_categories:
            errors['category'] = f'Invalid category. Must be one of: {", ".join(valid_categories)}'
    
    if errors:
        raise ValidationError(errors)
    
    return True

def calculate_total_price(property_id, check_in_date, check_out_date):
    """
    Calculate total price for a booking period
    """
    try:
        property = Property.objects.get(id=property_id)
        nights = (check_out_date - check_in_date).days
        if nights <= 0:
            raise ValueError("Check-out date must be after check-in date")
        
        total_price = property.price_per_night * nights
        return total_price
        
    except Property.DoesNotExist:
        raise ValueError("Property does not exist")
    except Exception as e:
        raise ValueError(f"Error calculating price: {str(e)}")

def get_properties_by_filters(filters):
    """
    Filter properties based on various criteria
    """
    queryset = Property.objects.all()
    
    # Category filter
    if filters.get('category'):
        queryset = queryset.filter(category=filters['category'])
    
    # Price range filter
    min_price = filters.get('min_price')
    max_price = filters.get('max_price')
    if min_price is not None:
        queryset = queryset.filter(price_per_night__gte=min_price)
    if max_price is not None:
        queryset = queryset.filter(price_per_night__lte=max_price)
    
    # Bedrooms filter
    if filters.get('bedrooms'):
        queryset = queryset.filter(bedrooms__gte=filters['bedrooms'])
    
    # Bathrooms filter
    if filters.get('bathrooms'):
        queryset = queryset.filter(bathrooms__gte=filters['bathrooms'])
    
    # Guests filter
    if filters.get('guests'):
        queryset = queryset.filter(guests__gte=filters['guests'])
    
    # Country filter
    if filters.get('country'):
        queryset = queryset.filter(country__icontains=filters['country'])
    
    # Favorited filter
    if filters.get('favorited') is not None:
        queryset = queryset.filter(favorited=filters['favorited'])
    
    # Search term filter
    if filters.get('search'):
        search_term = filters['search']
        queryset = queryset.filter(
            models.Q(title__icontains=search_term) |
            models.Q(description__icontains=search_term) |
            models.Q(country__icontains=search_term)
        )
    
    return queryset

def get_recently_added_properties(limit=6):
    """
    Get recently added properties (last 7 days)
    """
    one_week_ago = timezone.now() - timedelta(days=7)
    return Property.objects.filter(
        created_at__gte=one_week_ago
    ).order_by('-created_at')[:limit]

def get_popular_properties(limit=6):
    """
    Get popular properties (favorited by users)
    """
    return Property.objects.filter(
        favorited=True
    ).order_by('-created_at')[:limit]

def update_property_favorite_status(property_id, favorite):
    """
    Update favorite status of a property and clear cache
    """
    try:
        property = Property.objects.get(id=property_id)
        property.favorited = favorite
        property.save()
        
        # Clear the cache since properties data has changed
        cache.delete('all_properties')
        
        return property
    except Property.DoesNotExist:
        raise ValueError("Property does not exist")

def clear_properties_cache():
    """
    Clear the properties cache
    Useful when properties are added, updated, or deleted
    """
    cache.delete('all_properties')
    logger.debug("Properties cache cleared")

def get_property_statistics():
    """
    Get statistics about properties
    """
    total_properties = Property.objects.count()
    
    # Count by category
    categories = dict(Property.PROPERTY_CATEGORIES)
    category_stats = {}
    for category_code, category_name in categories.items():
        count = Property.objects.filter(category=category_code).count()
        category_stats[category_name] = count
    
    # Average price
    avg_price = Property.objects.aggregate(
        avg_price=models.Avg('price_per_night')
    )['avg_price'] or 0
    
    # Most expensive property
    most_expensive = Property.objects.order_by('-price_per_night').first()
    
    return {
        'total_properties': total_properties,
        'category_stats': category_stats,
        'average_price': round(avg_price, 2),
        'most_expensive_property': most_expensive.title if most_expensive else None,
        'max_price': most_expensive.price_per_night if most_expensive else 0
    }

def export_properties_to_csv(file_path):
    """
    Export all properties to CSV file
    """
    import csv
    from django.http import HttpResponse
    
    properties = get_all_properties()  # Use cached version if available
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'id', 'title', 'description', 'price_per_night', 'bedrooms',
            'bathrooms', 'guests', 'country', 'country_code', 'category',
            'favorited', 'created_at'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for prop in properties:
            writer.writerow({
                'id': prop.id,
                'title': prop.title,
                'description': prop.description,
                'price_per_night': prop.price_per_night,
                'bedrooms': prop.bedrooms,
                'bathrooms': prop.bathrooms,
                'guests': prop.guests,
                'country': prop.country,
                'country_code': prop.country_code,
                'category': prop.category,
                'favorited': prop.favorited,
                'created_at': prop.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return file_path

def import_properties_from_csv(file_path):
    """
    Import properties from CSV file and clear cache
    """
    import csv
    from django.db import transaction
    
    imported_count = 0
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, 2):  # Start from 2 (header is row 1)
                    try:
                        # Validate required fields
                        required_fields = ['title', 'price_per_night', 'bedrooms', 'bathrooms', 'guests', 'country']
                        for field in required_fields:
                            if not row.get(field):
                                errors.append(f"Row {row_num}: Missing required field '{field}'")
                                continue
                        
                        # Create or update property
                        property, created = Property.objects.update_or_create(
                            title=row['title'],
                            defaults={
                                'description': row.get('description', ''),
                                'price_per_night': float(row['price_per_night']),
                                'bedrooms': int(row['bedrooms']),
                                'bathrooms': int(row['bathrooms']),
                                'guests': int(row['guests']),
                                'country': row['country'],
                                'country_code': row.get('country_code') or get_country_code(row['country']),
                                'category': row.get('category', 'house'),
                                'favorited': row.get('favorited', '').lower() == 'true'
                            }
                        )
                        
                        if created:
                            imported_count += 1
                            
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
    
    except Exception as e:
        errors.append(f"File error: {str(e)}")
    
    # Clear cache after import
    clear_properties_cache()
    
    return {
        'imported_count': imported_count,
        'errors': errors,
        'success': len(errors) == 0
    }


