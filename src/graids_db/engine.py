"""In-memory database setup for the public offline example.

This file is **new demo scaffolding**, not the production database engine.
It deliberately knows nothing about live Discord credentials or databases.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from .models import Base

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None
_transaction_lock = asyncio.Lock()


async def connect_demo() -> None:
    """Create a temporary database. Nothing is saved to disk."""
    global _engine, _session_factory
    if _engine is not None:
        raise RuntimeError("Demo database is already connected")

    # StaticPool shares the same in-memory SQLite database across sessions.
    _engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", poolclass=StaticPool
    )
    _session_factory = async_sessionmaker(
        _engine, expire_on_commit=False
    )
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_demo() -> None:
    """Dispose of the temporary database after a test or demo run."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


@asynccontextmanager
async def transaction() -> AsyncIterator[AsyncSession]:
    """Match the transaction interface of the selected production module."""
    if _session_factory is None:
        raise RuntimeError("Call connect_demo() before database operations")
    # SQLite supports a single writer; keep the example simple and serial.
    async with _transaction_lock:
        async with _session_factory() as session:
            async with session.begin():
                yield session
