import asyncio
import logging
import random
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.redis import get_redis
from app.models import TicketTier

logger = logging.getLogger("ticketing.concurrency")

# Lua script to release Redis lock only if the token matches
# This guarantees that a slow client whose lock expired won't accidentally release
# a lock subsequently acquired by a new client.
LUA_RELEASE_LOCK = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


class LockAcquisitionError(Exception):
    """Raised when distributed lock cannot be acquired within timeout."""
    pass


class InsufficientInventoryError(Exception):
    """Raised when available ticket quantity is insufficient for requested booking."""
    pass


@asynccontextmanager
async def distributed_lock(
    resource_key: str,
    timeout_seconds: int = 10,
    blocking_timeout_seconds: float = 5.0,
    retry_interval_seconds: float = 0.05,
) -> AsyncGenerator[str, None]:
    """
    Distributed Lock implementation using Redis with:
    - Unique token-based ownership
    - Expiration TTL to prevent deadlocks
    - Atomic Lua release script
    - Jittered exponential backoff retry loop
    - Multi-process and multi-worker safety
    """
    redis = await get_redis()
    lock_key = f"lock:{resource_key}"
    token = str(uuid.uuid4())
    acquired = False
    start_time = asyncio.get_event_loop().time()

    try:
        while True:
            # Atomic SETNX with expiration TTL
            is_set = await redis.set(lock_key, token, ex=timeout_seconds, nx=True)
            if is_set:
                acquired = True
                logger.debug("Acquired distributed lock on %s (token=%s)", lock_key, token)
                break

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= blocking_timeout_seconds:
                logger.warning(
                    "Timed out waiting for lock on %s after %.2fs",
                    lock_key,
                    elapsed
                )
                raise LockAcquisitionError(
                    f"System busy: High demand on selected tickets. Could not acquire lock for {resource_key}."
                )

            # Jittered sleep to avoid thundering herd
            jitter = random.uniform(0.01, 0.05)
            await asyncio.sleep(retry_interval_seconds + jitter)

        yield token

    finally:
        if acquired:
            try:
                # Release lock atomically only if token matches
                await redis.eval(LUA_RELEASE_LOCK, 1, lock_key, token)
                logger.debug("Released distributed lock on %s", lock_key)
            except Exception as e:
                logger.error("Error releasing distributed lock for %s: %s", lock_key, e)


async def acquire_ticket_tier_for_update(
    db: AsyncSession,
    tier_id: str
) -> TicketTier:
    """
    Acquire row-level exclusive lock (SELECT ... FOR UPDATE) on TicketTier table.
    Provides defense-in-depth relational concurrency lock within the database transaction.
    """
    stmt = (
        select(TicketTier)
        .where(TicketTier.id == tier_id)
        .with_for_update()
    )
    result = await db.execute(stmt)
    tier = result.scalar_one_or_none()
    if not tier:
        raise ValueError(f"TicketTier with id {tier_id} not found.")
    return tier

