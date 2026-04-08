"""
OrcheFlowAI — Database Session Factory
Async SQLAlchemy engine configured for AlloyDB / Cloud SQL Postgres
"""
import os
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://orcheflow:orcheflow_dev@localhost:5432/postgres"
).strip()

# Robustness: Ensure asyncpg driver is used for Cloud Run / SQL instances
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

def create_robust_engine(url: str):
    """Factory for generating a working async engine with auto-fallback."""
    try:
        # For Postgres/AlloyDB
        if "postgresql" in url:
            return create_async_engine(
                url,
                pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
                max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
                echo=False,
                future=True,
            )
        # For SQLite fallback
        return create_async_engine(url, echo=False)
    except Exception:
        return create_async_engine("sqlite+aiosqlite:///local_demo.db", echo=False)

# Global engine instance
engine = create_robust_engine(DATABASE_URL)

AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

from db.base import Base

async def init_db():
    """Idempotent database initialization — ensures tables exist for either Postgres or SQLite."""
    import db.models  # Ensure models are registered with Base metadata
    try:
        # Diagnostic: Who and where are we?
        async with engine.connect() as conn:
            if engine.dialect.name == "postgresql":
                res = await conn.execute(text("SELECT current_database(), current_user"))
                db_info = res.fetchone()
                print(f"!! [DATABASE] Dialect: postgresql | Context: {db_info}")
                
                # Step 1: Extensions (Postgres only)
                print("!! [DATABASE] Attempting to ensure 'vector' extension exists...")
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                await conn.commit()
                print("!! [DATABASE] Extension 'vector' verified/created.")
            else:
                print(f"!! [DATABASE] Dialect: {engine.dialect.name} | Local Fallback Active")

        # Step 2: Table Creation
        print(f"!! [DATABASE] Syncing models (create_all) on {engine.dialect.name}...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        print(f"!! [DATABASE] Initialization complete for {engine.dialect.name}")
    except Exception as e:
        print(f"!! [DATABASE] Initialization error: {e}")

async def get_db() -> AsyncSession:
    """FastAPI dependency — yields a resilient async DB session with auto-fallback."""
    global engine, AsyncSessionFactory
    
    # Pre-flight check: Is the current engine working?
    use_fallback = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"!! [RECOVERY] DB Connectivity issue detected: {e}")
        use_fallback = True

    if use_fallback and engine.dialect.name == "postgresql":
        print("!! [RECOVERY] Attempting Auto-switch to Local SQLite for 2026 demo stability...")
        try:
            engine = create_async_engine("sqlite+aiosqlite:///local_demo.db", echo=False)
            AsyncSessionFactory = async_sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False, 
                autocommit=False, autoflush=False
            )
            await init_db()
        except Exception as recovery_e:
            print(f"!! [RECOVERY] SQLite Fallback failed: {recovery_e}")
            raise recovery_e

    # Yield the session (from either Postgres or SQLite engine)
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
