"""Dépendances FastAPI (utilisateur courant, rôle admin, clé n8n).

Périmètre : Yassine (feature/api-auth-n8n).

À implémenter :
- get_current_user(...)  -> User (401 si token absent/invalide)
- require_admin(...)     -> User (403 si role != admin)
- require_n8n_key(...)   -> None (401 si header X-API-Key != N8N_API_KEY)
"""
