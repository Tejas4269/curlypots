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


class Slot(models.Model):
    id = models.UUIDField(primary_key=True)

    slot_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    capacity = models.IntegerField()
    status = models.CharField(max_length=50)

    cancellation_reason = models.TextField(
        null=True,
        blank=True,
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "slots"
        managed = False
        ordering = ["slot_date", "start_time"]

    def __str__(self):
        return (
            f"{self.slot_date} "
            f"{self.start_time} - {self.end_time}"
        )