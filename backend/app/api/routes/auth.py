"""Routes /auth — périmètre : Yassine (feature/api-auth-n8n). Voir mission + schemas.py."""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])
