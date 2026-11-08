"""Client Groq (modèle configuré via GROQ_MODEL, par défaut qwen/qwen3.8-27b).

Périmètre : tech lead (feature/rag-core).
Point d'attention : retirer le raisonnement éventuel (<think>...</think>) de la réponse.
"""


def generate(
    messages: list[dict], temperature: float | None = None, max_tokens: int | None = None
) -> str:
    raise NotImplementedError("Implémenté dans feature/rag-core")
