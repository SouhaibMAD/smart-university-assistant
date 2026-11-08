"""Embeddings locaux (Groq ne propose pas d'endpoint d'embeddings).

Périmètre : tech lead (feature/rag-core).

Contrat :
- embed_passages(texts) -> vecteurs normalisés (indexation)
- embed_query(text)     -> vecteur normalisé (requête)
Les modèles e5 exigent les préfixes "passage: " et "query: ".
"""


def embed_passages(texts: list[str]) -> list[list[float]]:
    raise NotImplementedError("Implémenté dans feature/rag-core")


def embed_query(text: str) -> list[float]:
    raise NotImplementedError("Implémenté dans feature/rag-core")
