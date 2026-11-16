from datetime import datetime

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.orm import Session, aliased

from app.db.models import (
    Chunk,
    Conversation,
    Document,
    Message,
    User,
)


def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return db.scalar(statement)


def create_user(
    db: Session,
    username: str,
    password_hash: str,
    role: str = "student",
) -> User:
    user = User(
        username=username,
        password_hash=password_hash,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create_document(
    db: Session,
    filename: str,
    file_type: str,
    sha256: str,
    size_bytes: int,
    uploaded_by: int | None = None,
) -> Document:
    document = Document(
        filename=filename,
        file_type=file_type,
        sha256=sha256,
        size_bytes=size_bytes,
        uploaded_by=uploaded_by,
        status="processing",
        num_chunks=0,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_document(db: Session, document_id: int) -> Document | None:
    return db.get(Document, document_id)


def get_document_by_sha256(db: Session, sha256: str) -> Document | None:
    statement = select(Document).where(Document.sha256 == sha256)
    return db.scalar(statement)


def list_documents(db: Session) -> list[Document]:
    statement = select(Document).order_by(desc(Document.created_at))
    return list(db.scalars(statement).all())


def delete_document(db: Session, document_id: int) -> bool:
    document = db.get(Document, document_id)

    if document is None:
        return False

    db.delete(document)
    db.commit()
    return True

def add_chunks(
    db: Session,
    document_id: int,
    chunks: list[dict],
) -> list[Chunk]:
    db_chunks = [
        Chunk(
            document_id=document_id,
            chunk_index=chunk["chunk_index"],
            page=chunk.get("page"),
            content=chunk["content"],
            embedding=chunk.get("embedding"),
        )
        for chunk in chunks
    ]

    db.add_all(db_chunks)
    db.commit()

    for chunk in db_chunks:
        db.refresh(chunk)

    return db_chunks



def create_conversation(
    db: Session,
    user_id: int,
    title: str,
) -> Conversation:
    conversation = Conversation(
        user_id=user_id,
        title=title,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(
    db: Session,
    conversation_id: int,
) -> Conversation | None:
    return db.get(Conversation, conversation_id)


def list_conversations(
    db: Session,
    user_id: int,
) -> list[Conversation]:
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(desc(Conversation.updated_at))
    )
    return list(db.scalars(statement).all())


def delete_conversation(db: Session, conversation_id: int) -> bool:
    conversation = db.get(Conversation, conversation_id)

    if conversation is None:
        return False

    db.delete(conversation)
    db.commit()
    return True



def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
    sources: dict | list | None = None,
    answered: bool | None = None,
    latency_ms: int | None = None,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources,
        answered=answered,
        latency_ms=latency_ms,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_messages(
    db: Session,
    conversation_id: int,
) -> list[Message]:
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at, Message.id)
    )
    return list(db.scalars(statement).all())




def list_unanswered_questions(
    db: Session,
    since: datetime,
) -> list[Message]:
    next_assistant = aliased(Message)
    earlier_assistant = aliased(Message)

    next_after_user = or_(
        next_assistant.created_at > Message.created_at,
        and_(
            next_assistant.created_at == Message.created_at,
            next_assistant.id > Message.id,
        ),
    )

    earlier_than_next = or_(
        earlier_assistant.created_at < next_assistant.created_at,
        and_(
            earlier_assistant.created_at == next_assistant.created_at,
            earlier_assistant.id < next_assistant.id,
        ),
    )

    next_assistant_is_unanswered = (
        select(next_assistant.id)
        .where(
            next_assistant.conversation_id == Message.conversation_id,
            next_assistant.role == "assistant",
            next_assistant.answered.is_(False),
            next_after_user,
            ~select(earlier_assistant.id)
            .where(
                earlier_assistant.conversation_id == Message.conversation_id,
                earlier_assistant.role == "assistant",
                or_(
                    earlier_assistant.created_at > Message.created_at,
                    and_(
                        earlier_assistant.created_at == Message.created_at,
                        earlier_assistant.id > Message.id,
                    ),
                ),
                earlier_than_next,
            )
            .exists(),
        )
        .exists()
    )

    statement = select(Message).where(
        Message.role == "user",
        Message.created_at >= since,
        next_assistant_is_unanswered,
    )

    return list(db.scalars(statement).all())