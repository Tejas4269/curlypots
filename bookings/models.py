import uuid

from django.db import models
from django.utils import timezone

from customers.models import Customer
from workshops.models import Slot, Workshop


class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING_PAYMENT", "Pending Payment"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
        ("REFUND_REQUIRED", "Refund Required"),
        ("REFUNDED", "Refunded"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("MANUAL_VERIFICATION", "Manual Verification"),
        ("REFUND_REQUIRED", "Refund Required"),
        ("REFUNDED", "Refunded"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.DO_NOTHING,
        related_name="bookings",
    )

    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.DO_NOTHING,
        related_name="bookings",
    )

    slot = models.ForeignKey(
        Slot,
        on_delete=models.DO_NOTHING,
        related_name="bookings",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    coupon_id = models.UUIDField(
        null=True,
        blank=True,
    )

    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
    )

    payment_expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        default=timezone.now,
    )

    updated_at = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        db_table = "bookings"
        managed = False
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.name} - {self.workshop.name}"


class BookingParticipant(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.DO_NOTHING,
        related_name="participants",
    )

    name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    email = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        db_table = "booking_participants"
        managed = False
        ordering = ["created_at"]

    def __str__(self):
        return self.name or "Unnamed participant"

    