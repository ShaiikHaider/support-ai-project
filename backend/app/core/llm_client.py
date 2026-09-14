"""
Thin wrapper around the chat LLM so every agent calls one consistent
interface, regardless of provider. Supports structured JSON output via
Pydantic models (used heavily by the Triage/Escalation/Reviewer agents).
"""
import json
import re
from typing import Type, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from openai import AsyncOpenAI, APIError, RateLimitError, APITimeoutError

from app.core.config import settings

T = TypeVar("T", bound=BaseModel)

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url=settings.LLM_BASE_URL, 
            api_key=settings.LLM_API_KEY,
            timeout=15.0  # Fail fast instead of hanging for 10 minutes
        )
    return _client


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((APIError, RateLimitError, APITimeoutError))
)
async def chat_completion(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    client = get_client()
    response = await client.chat.completions.create(
        model=settings.LLM_CHAT_MODEL,
        temperature=temperature,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""


from pydantic import BaseModel, ValidationError

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((APIError, RateLimitError, APITimeoutError, ValueError, json.JSONDecodeError, ValidationError))
)
async def structured_completion(system_prompt: str, user_prompt: str, schema: Type[T], temperature: float = 0.1) -> T:
    """Requests a JSON object matching `schema` and parses it. Falls back to
    a best-effort parse if the model wraps the JSON in prose/backticks."""
    client = get_client()
    response = await client.chat.completions.create(
        model=settings.LLM_CHAT_MODEL,
        temperature=temperature,
        max_tokens=2000,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": f"{system_prompt}\n\nRespond with ONLY a single valid JSON object — no prose, no markdown code fences matching this schema:\n{schema.model_json_schema()}",
            },
            {"role": "user", "content": user_prompt},
        ],
    )
    if not response.choices or response.choices[0].message.content is None:
        raise ValueError(f"LLM returned empty/null content. Response: {response}")
    raw = response.choices[0].message.content or "{}"
    
    if not raw or not raw.strip():
        raise ValueError(
            f"LLM returned empty content. Model: {settings.LLM_CHAT_MODEL}. "
            f"Full raw response object: {response}"
        )

    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            raise
    return schema.model_validate(data)


