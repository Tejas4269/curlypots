import asyncio

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Workshop


async def main():
    async with SessionLocal() as db:
        result = await db.execute(
            select(Workshop)
            .order_by(Workshop.name)
        )

        workshops = result.scalars().all()

        print("\nCurlyPots workshops:")
        print("-" * 60)

        for workshop in workshops:
            print(
                f"{workshop.name} | "
                f"₹{workshop.price} | "
                f"{workshop.duration_minutes} min | "
                f"active={workshop.active}"
            )


if __name__ == "__main__":
    asyncio.run(main())