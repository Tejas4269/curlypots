from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from bookings.models import Booking

from payments.services.payment_service import (
    verify_payment_signature,
    confirm_booking_payment,
    create_razorpay_order,
    verify_webhook_signature,
)


@require_POST
def create_payment_order(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
    )

    if booking.status != "PENDING_PAYMENT":
        return JsonResponse(
            {"error": "This booking is not awaiting payment."},
            status=400,
        )

    if booking.payment_status != "PENDING":
        return JsonResponse(
            {"error": "Payment cannot be initiated for this booking."},
            status=400,
        )

    try:
        result = create_razorpay_order(
            booking=booking,
        )

        razorpay_order = result["razorpay_order"]

        return JsonResponse({
            "booking_id": str(booking.id),
            "razorpay_order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "key_id": __import__("django.conf").conf.settings.RAZORPAY_KEY_ID,
        })

    except Exception as exc:
        return JsonResponse(
            {"error": str(exc)},
            status=500,
        )

from django.views.decorators.http import require_POST

from payments.models import Payment
from payments.services.payment_service import verify_payment_signature


@require_POST
def verify_payment(request):
    import json

    try:
        data = json.loads(request.body)

        razorpay_order_id = data["razorpay_order_id"]
        razorpay_payment_id = data["razorpay_payment_id"]
        razorpay_signature = data["razorpay_signature"]

        verify_payment_signature(
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
        )

        booking = confirm_booking_payment(
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            payment_response=data,
        )

        return JsonResponse({
            "success": True,
            "booking_id": str(booking.id),
            "status": booking.status,
        })

    except Exception:
        return JsonResponse(
            {
                "success": False,
                "error": "Payment verification failed.",
            },
            status=400,
        )

@csrf_exempt
@require_POST
def razorpay_webhook(request):
    signature = request.headers.get(
        "X-Razorpay-Signature"
    )

    if not signature:
        return JsonResponse(
            {"error": "Missing webhook signature."},
            status=400,
        )

    if not verify_webhook_signature(
        payload=request.body,
        signature=signature,
    ):
        return JsonResponse(
            {"error": "Invalid webhook signature."},
            status=400,
        )

    import json

    try:
        data = json.loads(request.body)

        event = data.get("event")

        if event != "payment.captured":
            return JsonResponse({
                "success": True,
                "ignored": True,
            })

        payment_entity = (
            data["payload"]["payment"]["entity"]
        )

        razorpay_order_id = payment_entity["order_id"]
        razorpay_payment_id = payment_entity["id"]

        booking = confirm_booking_payment(
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            payment_response=data,
        )

        return JsonResponse({
            "success": True,
            "booking_id": str(booking.id),
            "status": booking.status,
        })

    except Exception:
        return JsonResponse(
            {"error": "Webhook processing failed."},
            status=400,
        )