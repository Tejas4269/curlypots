from django.urls import path

from .views import (
    create_payment_order,
    verify_payment,
    razorpay_webhook,
)

urlpatterns = [
    path(
        "create-order/<uuid:booking_id>/",
        create_payment_order,
        name="create_payment_order",
    ),
    path(
        "verify/",
        verify_payment,
        name="verify_payment",
    ),
    path(
        "webhook/",
        razorpay_webhook,
        name="razorpay_webhook",
    ),
]