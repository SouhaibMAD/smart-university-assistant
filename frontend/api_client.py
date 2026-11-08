"""Client HTTP unique vers le backend FastAPI.

Périmètre : Hafsa (feature/streamlit-ui).
Règle : TOUS les appels HTTP passent par ce fichier. Aucun `import streamlit` ici.
"""
import os

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 60


class ApiError(Exception):
    """Erreur renvoyée par l'API, avec un message lisible par l'utilisateur."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def health() -> bool:
    try:
        return requests.get(f"{BACKEND_URL}/health", timeout=5).ok
    except requests.RequestException:
        return False
