from django.db import models
from django.utils import timezone

class Property(models.Model):
    PROPERTY_CATEGORIES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('hotel', 'Hotel'),
        ('villa', 'Villa'),
        ('cottage', 'Cottage'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    guests = models.IntegerField()
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    category = models.CharField(max_length=20, choices=PROPERTY_CATEGORIES)
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    favorited = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

