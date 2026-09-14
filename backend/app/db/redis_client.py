"""
Redis-backed short-term memory for multi-turn conversations.

Design:
- Each ticket's live conversation buffer is stored as a Redis list under
  key `memory:ticket:{ticket_id}`, holding the last N turns as JSON strings.
- TTL keeps memory "short-term": if a ticket goes cold, its scratch memory
  expires, while the full transcript remains permanently in PostgreSQL
  (TicketMessage) as the persistent ticket history.
- Also used as a fast cache for the customer-context lookups so the
  Customer Context Agent doesn't hit Postgres on every turn.
"""
import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings

_redis_pool: redis.Redis | None = None

MAX_TURNS_IN_MEMORY = 20


def get_redis() -> redis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_pool


async def append_turn(ticket_id: int, role: str, content: str) -> None:
    r = get_redis()
    key = f"memory:ticket:{ticket_id}"
    payload = json.dumps({"role": role, "content": content})
    await r.rpush(key, payload)
    await r.ltrim(key, -MAX_TURNS_IN_MEMORY, -1)
    await r.expire(key, settings.CONVERSATION_MEMORY_TTL_SECONDS)


async def get_recent_turns(ticket_id: int) -> list[dict[str, str]]:
    r = get_redis()
    key = f"memory:ticket:{ticket_id}"
    raw = await r.lrange(key, 0, -1)
    return [json.loads(item) for item in raw]


async def cache_customer_context(ticket_id: int, context: dict[str, Any]) -> None:
    r = get_redis()
    await r.set(
        f"context:ticket:{ticket_id}",
        json.dumps(context),
        ex=settings.CONVERSATION_MEMORY_TTL_SECONDS,
    )


async def get_cached_customer_context(ticket_id: int) -> dict[str, Any] | None:
    r = get_redis()
    raw = await r.get(f"context:ticket:{ticket_id}")
    return json.loads(raw) if raw else None


async def clear_ticket_memory(ticket_id: int) -> None:
    r = get_redis()
    await r.delete(f"memory:ticket:{ticket_id}", f"context:ticket:{ticket_id}")
