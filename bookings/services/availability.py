from django.utils import timezone
from django.db.models import Q

from bookings.models import BookingParticipant


def get_slot_availability(slot):
    """
    Return the availability information for a workshop slot.
    """

    now = timezone.localtime()

    # Past dates are unavailable.
    if slot.slot_date < now.date():
        return {
            "available": False,
            "capacity": slot.capacity,
            "booked": 0,
            "remaining": 0,
            "reason": "past",
        }

    # Today's slot cannot be booked once it has started.
    if slot.slot_date == now.date() and slot.start_time <= now.time():
        return {
            "available": False,
            "capacity": slot.capacity,
            "booked": 0,
            "remaining": 0,
            "reason": "started",
        }

    # Cancelled slots are unavailable.
    if slot.status != "OPEN":
        return {
            "available": False,
            "capacity": slot.capacity,
            "booked": 0,
            "remaining": 0,
            "reason": "cancelled",
        }

    now = timezone.now()

    # CONFIRMED bookings + active payment holds consume capacity.
    booked = BookingParticipant.objects.filter(
        booking__slot=slot,
    ).filter(
        Q(booking__status="CONFIRMED")
        | Q(
            booking__status="PENDING_PAYMENT",
            booking__payment_expires_at__gt=now,
        )
    ).count()

    remaining = max(slot.capacity - booked, 0)

    return {
        "available": remaining > 0,
        "capacity": slot.capacity,
        "booked": booked,
        "remaining": remaining,
        "reason": None if remaining > 0 else "full",
    }