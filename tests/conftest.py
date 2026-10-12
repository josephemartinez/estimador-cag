import fakeredis
import pytest

from app.config import Settings
from app.services.cache import EstimationCache
from app.services.llm_wrapper import LLMWrapper


@pytest.fixture
def cache():
    return EstimationCache(fakeredis.FakeRedis(decode_responses=True), ttl=60)


@pytest.fixture
def wrapper(cache):
    settings = Settings(_env_file=None, ANTHROPIC_API_KEY="test")
    return LLMWrapper(settings=settings, cache=cache)