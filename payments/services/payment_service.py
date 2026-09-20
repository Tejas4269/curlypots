import razorpay

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from bookings.models import Booking
from payments.models import Payment

import hmac
import hashlib


def get_razorpay_client():
    return razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )


@transaction.atomic
def create_razorpay_order(*, booking):
    if (
        booking.payment_expires_at is not None
        and booking.payment_expires_at <= timezone.now()
    ):
        raise ValueError("This booking payment hold has expired.")

    client = get_razorpay_client()

    razorpay_order = client.order.create({
        "amount": int(booking.total_amount * 100),
        "currency": "INR",
        "receipt": str(booking.id),
        "notes": {
            "booking_id": str(booking.id),
        },
    })

    now = timezone.now()

    payment = Payment.objects.create(
        booking=booking,
        provider="RAZORPAY",
        provider_order_id=razorpay_order["id"],
        amount=booking.total_amount,
        currency="INR",
        status="PENDING",
        raw_response=razorpay_order,
        created_at=now,
        updated_at=now,
    )

    return {
        "payment": payment,
        "razorpay_order": razorpay_order,
    }


def verify_payment_signature(
    *,
    razorpay_order_id,
    razorpay_payment_id,
    razorpay_signature,
):
    client = get_razorpay_client()

    client.utility.verify_payment_signature({
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    })

    return True


@transaction.atomic
def confirm_booking_payment(
    *,
    razorpay_order_id,
    razorpay_payment_id,
    payment_response,
):
    payment = (
        Payment.objects
        .select_for_update()
        .select_related("booking")
        .get(
            provider="RAZORPAY",
            provider_order_id=razorpay_order_id,
        )
    )

    booking = (
        Booking.objects
        .select_for_update()
        .get(pk=payment.booking_id)
    )

    if payment.status == "SUCCESS" and booking.status == "CONFIRMED":
        return booking

    now = timezone.now()

    if (
        booking.payment_expires_at is not None
        and booking.payment_expires_at <= now
    ):
        booking.status = "REFUND_REQUIRED"
        booking.payment_status = "REFUND_REQUIRED"
        booking.updated_at = now
        booking.save(
            update_fields=[
                "status",
                "payment_status",
                "updated_at",
            ]
        )

        raise ValueError(
            "Payment was received after the booking hold expired. "
            "Refund is required."
        )

    payment.provider_payment_id = razorpay_payment_id
    payment.status = "SUCCESS"
    payment.raw_response = payment_response
    payment.updated_at = now

    payment.save(
        update_fields=[
            "provider_payment_id",
            "status",
            "raw_response",
            "updated_at",
        ]
    )

    booking.status = "CONFIRMED"
    booking.payment_status = "PAID"
    booking.updated_at = now

    booking.save(
        update_fields=[
            "status",
            "payment_status",
            "updated_at",
        ]
    )

    return booking

def verify_webhook_signature(*, payload, signature):
    expected_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature,
    )