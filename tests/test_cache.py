import redis

from app.services.cache import EstimationCache


def _key(**cambios):
    base = dict(system_prompt="s", user_message="u", model="m", max_tokens=10, temperature=0.2)
    return EstimationCache.make_key(**{**base, **cambios})


def test_la_clave_es_determinista():
    assert _key() == _key()
    assert _key().startswith("estimation:")


def test_la_clave_cambia_si_cambia_el_texto():
    assert _key() != _key(user_message="otro texto")
    assert _key() != _key(system_prompt="otro prompt")


def test_guarda_y_devuelve(cache):
    cache.set("k", {"estimation": "hola"})
    assert cache.get("k") == {"estimation": "hola"}


def test_clave_inexistente_devuelve_none(cache):
    assert cache.get("no-existe") is None


class RedisCaido:
    def get(self, key):
        raise redis.ConnectionError("caido")

    def set(self, *args, **kwargs):
        raise redis.ConnectionError("caido")

def test_si_redis_se_cae_no_rompe():
    cache = EstimationCache(RedisCaido())
    assert cache.get("k") is None
    cache.set("k", {"a": 1})  # no debe lanzar excepcion