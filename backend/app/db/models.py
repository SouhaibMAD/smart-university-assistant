"""Modèles SQLAlchemy 2.0.

Périmètre : Siham (feature/db-ingestion).

Tables à définir (spécification exacte dans la mission) :
users, documents, chunks (colonne embedding = Vector(settings.embedding_dim)),
conversations, messages.
"""
from app.db.base import Base  # noqa: F401
