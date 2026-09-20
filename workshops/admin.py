from django.contrib import admin

from .models import Slot, Workshop


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "duration_minutes",
        "active",
    )
    list_filter = ("active",)
    search_fields = ("name", "slug")


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = (
        "slot_date",
        "start_time",
        "end_time",
        "capacity",
        "status",
    )

    list_filter = (
        "slot_date",
        "status",
    )

    ordering = (
        "slot_date",
        "start_time",
    )