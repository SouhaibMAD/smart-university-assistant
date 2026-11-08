from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import auth, chat, conversations, documents, health, internal
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Smart University Assistant",
    description="Assistant RAG pour l'information universitaire.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(internal.router)
