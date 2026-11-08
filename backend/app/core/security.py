"""Hachage des mots de passe et JWT.

Périmètre : Yassine (feature/api-auth-n8n).

À implémenter :
- hash_password(password) -> str
- verify_password(password, password_hash) -> bool
- create_access_token(user_id, username, role) -> str
- decode_access_token(token) -> dict   (lève ValueError si invalide ou expiré)
"""


def hash_password(password: str) -> str:
    raise NotImplementedError


def verify_password(password: str, password_hash: str) -> bool:
    raise NotImplementedError


def create_access_token(user_id: int, username: str, role: str) -> str:
    raise NotImplementedError


def decode_access_token(token: str) -> dict:
    raise NotImplementedError
