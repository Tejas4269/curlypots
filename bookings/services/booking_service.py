from decimal import Decimal
from uuid import uuid4
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.db.models import Q

from bookings.models import Booking, BookingParticipant
from coupons.models import Coupon
from coupons.services.coupon_service import calculate_discount
from customers.models import Customer
from workshops.models import Slot, Workshop


@transaction.atomic
def create_booking(
    *,
    customer,
    workshop,
    slot,
    participants,
    coupon=None,
):
    """
    Create a pending-payment booking.

    The slot is locked during the transaction so concurrent
    bookings cannot oversell the available capacity.
    """

    slot = (
        Slot.objects
        .select_for_update()
        .get(pk=slot.pk)
    )

    now = timezone.localtime()

    if slot.status != "OPEN":
        raise ValueError("This slot is not available.")

    if slot.slot_date < now.date():
        raise ValueError("This slot has already passed.")

    if (
        slot.slot_date == now.date()
        and slot.start_time <= now.time()
    ):
        raise ValueError("This slot has already started.")

    if not workshop.active:
        raise ValueError(
            "This workshop is currently unavailable."
        )

    if not participants:
        raise ValueError(
            "At least one participant is required."
        )

    requested_seats = len(participants)

    # CONFIRMED bookings + active payment holds consume capacity.
    current_time = timezone.now()

    booked_seats = BookingParticipant.objects.filter(
        booking__slot=slot,
    ).filter(
        Q(booking__status="CONFIRMED")
        | Q(
            booking__status="PENDING_PAYMENT",
            booking__payment_expires_at__gt=current_time,
        )
    ).count()

    remaining_seats = slot.capacity - booked_seats

    if requested_seats > remaining_seats:
        raise ValueError(
            f"Only {remaining_seats} seat(s) are available."
        )

    subtotal = (
        workshop.price * requested_seats
    )

    discount_amount = Decimal("0.00")
    total_amount = subtotal
    coupon_id = None

    if coupon is not None:
        coupon_result = calculate_discount(
            coupon=coupon,
            subtotal=subtotal,
        )

        discount_amount = coupon_result["discount"]
        total_amount = coupon_result["total"]
        coupon_id = coupon.id

    current_time = timezone.now()
    payment_expires_at = current_time + timedelta(minutes=10)
    
    booking = Booking.objects.create(
        id=uuid4(),
        customer=customer,
        workshop=workshop,
        slot=slot,
        status="PENDING_PAYMENT",
        subtotal=subtotal,
        discount_amount=discount_amount,
        total_amount=total_amount,
        coupon_id=coupon_id,
        payment_status="PENDING",
        created_at=current_time,
        updated_at=current_time,
    )

    BookingParticipant.objects.bulk_create(
        [
            BookingParticipant(
                id=uuid4(),
                booking=booking,
                name=participant.get("name"),
                phone=participant.get("phone"),
                email=participant.get("email"),
                created_at=current_time,
            )
            for participant in participants
        ]
    )

    return booking