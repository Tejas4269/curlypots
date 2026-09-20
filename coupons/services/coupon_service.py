from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from coupons.models import Coupon


class CouponError(Exception):
    """Raised when a coupon cannot be applied."""


def calculate_discount(*, coupon, subtotal):
    """
    Validate a coupon and calculate the discount.
    """

    subtotal = Decimal(str(subtotal))

    if subtotal <= Decimal("0"):
        raise CouponError("Subtotal must be greater than zero.")

    if not coupon.active:
        raise CouponError("This coupon is inactive.")

    now = timezone.now()

    if coupon.valid_from and now < coupon.valid_from:
        raise CouponError("This coupon is not active yet.")

    if coupon.valid_until and now > coupon.valid_until:
        raise CouponError("This coupon has expired.")

    if (
        coupon.usage_limit is not None
        and coupon.usage_count >= coupon.usage_limit
    ):
        raise CouponError("This coupon has reached its usage limit.")

    minimum_order_amount = Decimal(
        str(coupon.minimum_order_amount)
    )

    if subtotal < minimum_order_amount:
        raise CouponError(
            f"Minimum order amount is ₹{minimum_order_amount}."
        )

    discount_value = Decimal(
        str(coupon.discount_value)
    )

    if coupon.discount_type == "PERCENTAGE":
        discount = (
            subtotal
            * discount_value
            / Decimal("100")
        )

    elif coupon.discount_type == "FLAT":
        discount = discount_value

    else:
        raise CouponError("Invalid coupon discount type.")

    if coupon.max_discount_amount is not None:
        max_discount = Decimal(
            str(coupon.max_discount_amount)
        )

        discount = min(
            discount,
            max_discount,
        )

    # Ensure Decimal even if the database/model supplied
    # an integer value.
    discount = Decimal(str(discount))

    # Discount cannot exceed subtotal.
    discount = min(
        discount,
        subtotal,
    )

    discount = Decimal(str(discount)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    total = subtotal - discount

    return {
        "coupon": coupon,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
    }