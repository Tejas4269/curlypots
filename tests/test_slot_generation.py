import asyncio

from app.database import SessionLocal
from app.services.slot_service import generate_slots


async def main():
    async with SessionLocal() as db:
        created = await generate_slots(db)

        print(f"New slots created: {created}")


if __name__ == "__main__":
    asyncio.run(main())