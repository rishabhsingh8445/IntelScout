import asyncio
from sqlalchemy import text
from src.database import engine

async def migrate():
    print("Running PostgreSQL migration for V3 Sentiment columns...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE competitor_snapshots ADD COLUMN sentiment VARCHAR;"))
            print("Added sentiment column.")
        except Exception as e:
            print(f"sentiment column might exist: {e}")
            
        try:
            await conn.execute(text("ALTER TABLE competitor_snapshots ADD COLUMN sentiment_score FLOAT;"))
            print("Added sentiment_score column.")
        except Exception as e:
            print(f"sentiment_score column might exist: {e}")
            
        try:
            await conn.execute(text("ALTER TABLE competitor_snapshots ADD COLUMN sentiment_reason TEXT;"))
            print("Added sentiment_reason column.")
        except Exception as e:
            print(f"sentiment_reason column might exist: {e}")
            
    print("Migration complete!")

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(migrate())
