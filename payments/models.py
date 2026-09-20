import uuid

from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    booking = models.ForeignKey(
        "bookings.Booking",
        db_column="booking_id",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="payments",
    )

    order_id = models.UUIDField(
        null=True,
        blank=True,
    )

    provider = models.CharField(max_length=255)
    provider_order_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    provider_payment_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    currency = models.CharField(max_length=50)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
    )

    raw_response = models.JSONField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "payments"
        managed = False

    def __str__(self):
        return f"{self.provider} - {self.amount} - {self.status}"