import asyncio
import logging
import uuid
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("ticketing.redis")

# Global async redis connection pool
redis_client: Optional[aioredis.Redis] = None


class InMemoryFallbackRedis:
    """
    In-memory fallback for local development or testing environments
    where an external Redis instance may not be immediately running.
    Provides identical async interface for locks and key-value storage.
    """
    def __init__(self):
        self._store = {}
        self._locks = {}
        self._lock_objects = {}

    async def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None, nx: bool = False) -> bool:
        if nx and key in self._store:
            return False
        self._store[key] = str(value)
        if ex:
            asyncio.create_task(self._expire_key(key, ex))
        return True

    async def _expire_key(self, key: str, delay: int):
        await asyncio.sleep(delay)
        self._store.pop(key, None)

    async def delete(self, *keys: str) -> int:
        deleted = 0
        for k in keys:
            if k in self._store:
                del self._store[k]
                deleted += 1
            if k in self._locks:
                del self._locks[k]
        return deleted

    async def eval(self, script: str, numkeys: int, *args):
        # Emulate token-matching unlock script
        if numkeys == 1 and len(args) >= 1:
            key = args[0]
            expected_val = args[1] if len(args) > 1 else None
            current_val = self._store.get(key)
            if current_val is not None and current_val == expected_val:
                del self._store[key]
                return 1
            return 0
        return 0

    def lock(self, name: str, timeout: Optional[float] = None, blocking_timeout: Optional[float] = None):
        return InMemoryLock(self, name, timeout, blocking_timeout)

    async def ping(self) -> bool:
        return True

    async def close(self):
        self._store.clear()
        self._locks.clear()


class InMemoryLock:
    def __init__(self, backend: InMemoryFallbackRedis, name: str, timeout: Optional[float] = 10, blocking_timeout: Optional[float] = 5):
        self.backend = backend
        self.name = name
        self.timeout = timeout or 10.0
        self.blocking_timeout = blocking_timeout or 5.0
        self.token = str(uuid.uuid4())
        self.acquired = False

    async def acquire(self) -> bool:
        start_time = asyncio.get_event_loop().time()
        while True:
            if self.name not in self.backend._locks:
                self.backend._locks[self.name] = self.token
                self.acquired = True
                if self.timeout:
                    asyncio.create_task(self._auto_release(self.token, self.timeout))
                return True
            if (asyncio.get_event_loop().time() - start_time) > self.blocking_timeout:
                return False
            await asyncio.sleep(0.05)

    async def _auto_release(self, token: str, delay: float):
        await asyncio.sleep(delay)
        if self.backend._locks.get(self.name) == token:
            del self.backend._locks[self.name]

    async def release(self):
        if self.backend._locks.get(self.name) == self.token:
            del self.backend._locks[self.name]
            self.acquired = False

    async def __aenter__(self):
        acquired = await self.acquire()
        if not acquired:
            raise TimeoutError(f"Could not acquire lock for {self.name} within timeout.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()


async def get_redis() -> aioredis.Redis:
    """Retrieve active Redis client, initializing or falling back if necessary."""
    global redis_client
    if redis_client is None:
        try:
            client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                protocol=2,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            await client.ping()
            redis_client = client
            logger.info("Successfully connected to Redis instance at %s", settings.REDIS_URL)
        except Exception as e:
            logger.warning(
                "Redis connection failed (%s). Falling back to resilient in-memory distributed lock emulator.",
                e
            )
            redis_client = InMemoryFallbackRedis()
    return redis_client


async def close_redis() -> None:
    """Close Redis connection on shutdown."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None

