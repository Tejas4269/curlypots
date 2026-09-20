from django.contrib import admin

from .models import Workshop


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