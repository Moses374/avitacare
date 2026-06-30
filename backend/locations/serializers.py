from rest_framework import serializers

from .models import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['location_id', 'level', 'county', 'sub_county', 'display_name']

    county = serializers.CharField(source='county_name', read_only=True)
    sub_county = serializers.CharField(source='sub_county_name', read_only=True)


class LocationIdField(serializers.SlugRelatedField):
    """Write a location by its public location_id (e.g. 'KE-47-LANGATA'), not its numeric pk."""

    def __init__(self, **kwargs):
        kwargs.setdefault('slug_field', 'location_id')
        kwargs.setdefault('queryset', Location.objects.all())
        super().__init__(**kwargs)
