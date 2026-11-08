"""Routes /chat — périmètre : Yassine (feature/api-auth-n8n). Voir mission + schemas.py."""
from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])
