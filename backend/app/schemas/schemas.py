"""Contrat d'API : schémas Pydantic partagés backend <-> frontend.

Propriété du tech lead. NE PAS MODIFIER sans accord.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Role = Literal["admin", "student"]


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    username: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: Role


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    file_type: str
    size_bytes: int
    num_pages: int | None = None
    num_chunks: int
    status: str
    created_at: datetime


class SourceOut(BaseModel):
    document_id: int
    document_name: str
    page: int | None = None
    excerpt: str
    score: float


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    conversation_id: int
    answer: str
    answered: bool
    sources: list[SourceOut]
    latency_ms: int


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: Literal["user", "assistant"]
    content: str
    sources: list[SourceOut] | None = None
    answered: bool | None = None
    created_at: datetime


class UnansweredQuestionOut(BaseModel):
    conversation_id: int
    question: str
    asked_at: datetime
