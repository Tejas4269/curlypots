from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Slot


SLOT_DURATION_MINUTES = 60
OPENING_HOUR = 11
CLOSING_HOUR = 21
DEFAULT_CAPACITY = 10
BOOKING_WINDOW_DAYS = 30


async def generate_slots(
    db: AsyncSession,
    start_date: date | None = None,
) -> int:
    """
    Generate slots for a 30-day booking window.

    Returns the number of newly created slots.
    """

    if start_date is None:
        start_date = date.today()

    created_count = 0

    for day_offset in range(BOOKING_WINDOW_DAYS):
        slot_date = start_date + timedelta(days=day_offset)

        for hour in range(OPENING_HOUR, CLOSING_HOUR):
            start_time = time(hour, 0)
            end_time = time(hour + 1, 0)

            existing_slot = await db.scalar(
                select(Slot).where(
                    Slot.slot_date == slot_date,
                    Slot.start_time == start_time,
                )
            )

            if existing_slot:
                continue

            slot = Slot(
                slot_date=slot_date,
                start_time=start_time,
                end_time=end_time,
                capacity=DEFAULT_CAPACITY,
                status="OPEN",
            )

            db.add(slot)
            created_count += 1

    await db.commit()

    return created_count