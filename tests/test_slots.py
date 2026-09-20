import asyncio

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Slot


async def main():
    async with SessionLocal() as db:
        result = await db.execute(
            select(Slot)
            .order_by(
                Slot.slot_date,
                Slot.start_time,
            )
        )

        slots = result.scalars().all()

        print("\nCurlyPots slots:")
        print("-" * 70)

        for slot in slots:
            print(
                f"{slot.slot_date} | "
                f"{slot.start_time} - {slot.end_time} | "
                f"capacity={slot.capacity} | "
                f"status={slot.status}"
            )


if __name__ == "__main__":
    asyncio.run(main())