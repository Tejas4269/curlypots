import asyncio

from app.database import test_connection


async def main():
    result = await test_connection()

    print("Supabase async connection successful!")
    print("SELECT 1 returned:", result)


if __name__ == "__main__":
    asyncio.run(main())