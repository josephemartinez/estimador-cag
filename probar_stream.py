import sys
import time

from app.logging_config import configure_logging
from app.services.llm_service import build_system_prompt
from app.services.llm_wrapper import LLMWrapper

sys.stdout.reconfigure(encoding="utf-8")
configure_logging()
texto = open("transcripcion_reunion.txt", encoding="utf-8").read()

inicio = time.perf_counter()
primero = None
for ev in LLMWrapper().complete_stream(system_prompt=build_system_prompt(), user_message=texto):
    if ev["type"] == "token":
        if primero is None:
            primero = time.perf_counter() - inicio
        print(ev["text"], end="", flush=True)
    else:
        print("\n\nMETA:", ev)
print(f"\nPrimer texto a los {primero:.1f} s")