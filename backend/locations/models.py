from django.db import models


class Location(models.Model):
    """A searchable Kenyan location: either a county or a sub-county within one.

    Ward and town/area levels are intentionally omitted: no verified dataset for
    them was available at build time (see locations/data/SOURCE.md). Adding them
    later only requires new rows with level='ward'/'town' and a parent.
    """

    class Level(models.TextChoices):
        COUNTY = 'county', 'County'
        SUB_COUNTY = 'sub_county', 'Sub-county'

    location_id = models.CharField(max_length=40, unique=True)
    level = models.CharField(max_length=20, choices=Level.choices)
    name = models.CharField(max_length=150)
    county_code = models.PositiveSmallIntegerField()
    county_name = models.CharField(max_length=150)
    sub_county_name = models.CharField(max_length=150, blank=True)
    display_name = models.CharField(max_length=300)

    class Meta:
        db_table = 'locations'
        ordering = ['county_name', 'sub_county_name']
        indexes = [
            models.Index(fields=['county_code']),
            models.Index(fields=['level']),
        ]

    def __str__(self):
        return self.display_name
