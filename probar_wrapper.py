from app.logging_config import configure_logging
from app.services.llm_service import build_system_prompt
from app.services.llm_wrapper import LLMWrapper

configure_logging()
texto = open("transcripcion_reunion.txt", encoding="utf-8").read()
r = LLMWrapper().complete(system_prompt=build_system_prompt(), user_message=texto)
print(r["estimation"][:300])
print({k: v for k, v in r.items() if k != "estimation"})