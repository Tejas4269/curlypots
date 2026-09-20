from django.contrib import admin

from .models import Booking, BookingParticipant


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "workshop",
        "slot",
        "status",
        "payment_status",
        "total_amount",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "workshop",
    )

    search_fields = (
        "customer__name",
        "customer__phone",
        "customer__email",
    )

    ordering = ("-created_at",)


@admin.register(BookingParticipant)
class BookingParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "email",
        "booking",
        "created_at",
    )

    search_fields = (
        "name",
        "phone",
        "email",
    )