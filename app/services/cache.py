import hashlib
import json

import redis
import structlog

log = structlog.get_logger()


class EstimationCache:
    def __init__(self, client: redis.Redis, ttl: int = 86400):
        self.client = client
        self.ttl = ttl

    @classmethod
    def from_url(cls, url: str, ttl: int = 86400) -> "EstimationCache":
        client = redis.from_url(url, decode_responses=True, socket_connect_timeout=2)
        return cls(client, ttl)

    @staticmethod
    def make_key(
        *, system_prompt: str, user_message: str, model: str, max_tokens: int, temperature: float
    ) -> str:
        payload = json.dumps(
            {
                "system_prompt": system_prompt,
                "user_message": user_message,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            sort_keys=True,
        )
        return "estimation:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, key: str) -> dict | None:
        try:
            cached = self.client.get(key)
        except redis.RedisError as exc:
            log.warning("cache_get_failed", error=str(exc))
            return None
        if cached:
            return json.loads(cached)
        return None

    def set(self, key: str, value: dict) -> None:
        try:
            self.client.set(key, json.dumps(value), ex=self.ttl)
        except redis.RedisError as exc:
            log.warning("cache_set_failed", error=str(exc))