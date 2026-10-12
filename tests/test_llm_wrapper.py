from types import SimpleNamespace

import pytest

from app.services.llm_wrapper import _cost, _provider


def _respuesta(texto="ok", modelo="claude-haiku-4-5-20251001"):
    return SimpleNamespace(
        model=modelo,
        usage=SimpleNamespace(prompt_tokens=100, completion_tokens=50),
        choices=[SimpleNamespace(message=SimpleNamespace(content=texto))],
    )


def _chunk(texto=None, usage=None, modelo="claude-haiku-4-5"):
    choices = [SimpleNamespace(delta=SimpleNamespace(content=texto))] if texto else []
    return SimpleNamespace(model=modelo, usage=usage, choices=choices)


class RouterFalso:
    def __init__(self, respuesta=None, chunks=None, error=None):
        self.respuesta, self.chunks, self.error, self.llamadas = respuesta, chunks, error, 0

    def completion(self, **kwargs):
        self.llamadas += 1
        if self.error:
            raise self.error
        return iter(self.chunks) if kwargs.get("stream") else self.respuesta


def _llamar(wrapper, texto="transcripcion"):
    return wrapper.complete(system_prompt="sistema", user_message=texto)


def test_complete_devuelve_estimacion_y_metricas(wrapper):
    wrapper.router = RouterFalso(respuesta=_respuesta("hola"))
    r = _llamar(wrapper)
    assert r["estimation"] == "hola"
    assert r["provider"] == "anthropic"
    assert (r["input_tokens"], r["output_tokens"]) == (100, 50)
    assert r["cost_usd"] == pytest.approx(0.00035)
    assert r["cache_hit"] is False


def test_la_segunda_llamada_igual_sale_del_cache(wrapper):
    wrapper.router = RouterFalso(respuesta=_respuesta())
    _llamar(wrapper)
    r2 = _llamar(wrapper)
    assert wrapper.router.llamadas == 1
    assert r2["cache_hit"] is True
    assert r2["cost_usd"] == 0.0


def test_otra_transcripcion_no_usa_el_cache(wrapper):
    wrapper.router = RouterFalso(respuesta=_respuesta())
    _llamar(wrapper, "uno")
    _llamar(wrapper, "dos")
    assert wrapper.router.llamadas == 2


def test_si_el_proveedor_falla_el_error_se_propaga(wrapper):
    wrapper.router = RouterFalso(error=RuntimeError("todos fallaron"))
    with pytest.raises(RuntimeError):
        _llamar(wrapper)


def test_stream_entrega_tokens_y_meta(wrapper):
    uso = SimpleNamespace(prompt_tokens=100, completion_tokens=50)
    wrapper.router = RouterFalso(chunks=[_chunk("Hola "), _chunk("mundo"), _chunk(usage=uso)])
    eventos = list(wrapper.complete_stream(system_prompt="s", user_message="t"))
    assert [e["text"] for e in eventos if e["type"] == "token"] == ["Hola ", "mundo"]
    meta = eventos[-1]
    assert meta["type"] == "meta"
    assert meta["input_tokens"] == 100
    assert meta["cache_hit"] is False


def test_stream_guarda_en_cache_y_la_repeticion_no_llama_al_modelo(wrapper):
    uso = SimpleNamespace(prompt_tokens=100, completion_tokens=50)
    wrapper.router = RouterFalso(chunks=[_chunk("Hola"), _chunk(usage=uso)])
    list(wrapper.complete_stream(system_prompt="s", user_message="t"))
    eventos = list(wrapper.complete_stream(system_prompt="s", user_message="t"))
    assert wrapper.router.llamadas == 1
    assert eventos[0]["text"] == "Hola"
    assert eventos[-1]["cache_hit"] is True


def test_proveedor_segun_el_modelo():
    assert _provider("claude-haiku-4-5") == "anthropic"
    assert _provider("gpt-4o-mini") == "openai"


def test_el_costo_funciona_con_sufijo_de_fecha():
    assert _cost("claude-haiku-4-5-20251001", 100, 50) is not None