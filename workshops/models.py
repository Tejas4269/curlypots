from django.db import models


class Workshop(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField()
    active = models.BooleanField()

    class Meta:
        db_table = "workshops"
        managed = False

    def __str__(self):
        return self.name