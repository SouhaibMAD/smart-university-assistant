
import uuid

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from app.db import crud
from app.db.models import (
    Chunk,
    Conversation,
    Document,
    Message,
    User,
)
from app.db.session import SessionLocal


def unique_value(prefix):
    return f"{prefix}_{uuid.uuid4().hex}"


def test_all_five_tables_exist():
    db = SessionLocal()

    try:
        inspector = inspect(db.bind)
        tables = set(inspector.get_table_names())

        assert {
            "users",
            "documents",
            "chunks",
            "conversations",
            "messages",
        }.issubset(tables)
    finally:
        db.close()


def test_user_crud_operations():
    db = SessionLocal()
    username = unique_value("student")

    try:
        user = crud.create_user(db, username, "hashed_password")

        assert user.id is not None
        assert user.role == "student"
        assert crud.get_user(db, user.id).username == username
        assert crud.get_user_by_username(db, username).id == user.id
    finally:
        user = crud.get_user_by_username(db, username)
        if user:
            db.delete(user)
            db.commit()
        db.close()


def test_duplicate_username_is_rejected():
    db = SessionLocal()
    username = unique_value("duplicate_user")

    try:
        crud.create_user(db, username, "password_hash")

        db.add(User(username=username, password_hash="another_hash"))

        with pytest.raises(IntegrityError):
            db.commit()

        db.rollback()
    finally:
        user = crud.get_user_by_username(db, username)
        if user:
            db.delete(user)
            db.commit()
        db.close()


def test_document_crud_operations():
    db = SessionLocal()
    sha256 = uuid.uuid4().hex * 2

    try:
        document = crud.create_document(
            db=db,
            filename="test.txt",
            file_type="txt",
            sha256=sha256,
            size_bytes=100,
        )

        assert document.id is not None
        assert document.status == "processing"
        assert document.num_chunks == 0

        assert crud.get_document(db, document.id).id == document.id
        assert crud.get_document_by_sha256(db, sha256).id == document.id
        assert document in crud.list_documents(db)

    finally:
        document = crud.get_document_by_sha256(db, sha256)
        if document:
            db.delete(document)
            db.commit()
        db.close()


def test_duplicate_document_hash_is_rejected():
    db = SessionLocal()
    sha256 = uuid.uuid4().hex * 2

    try:
        crud.create_document(
            db, "first.txt", "txt", sha256, 100
        )

        db.add(
            Document(
                filename="second.txt",
                file_type="txt",
                sha256=sha256,
                size_bytes=100,
            )
        )

        with pytest.raises(IntegrityError):
            db.commit()

        db.rollback()

    finally:
        document = crud.get_document_by_sha256(db, sha256)
        if document:
            db.delete(document)
            db.commit()
        db.close()


def test_document_deletion_cascades_to_chunks():
    db = SessionLocal()
    sha256 = uuid.uuid4().hex * 2

    try:
        document = crud.create_document(
            db, "cascade_test.txt", "txt", sha256, 100
        )

        chunks = crud.add_chunks(
            db,
            document.id,
            [
                {
                    "chunk_index": 0,
                    "content": "First test chunk",
                },
                {
                    "chunk_index": 1,
                    "content": "Second test chunk",
                },
            ],
        )

        chunk_ids = [chunk.id for chunk in chunks]

        assert len(chunk_ids) == 2

        assert crud.delete_document(db, document.id) is True

        remaining_chunks = db.scalars(
            select(Chunk).where(Chunk.id.in_(chunk_ids))
        ).all()

        assert remaining_chunks == []
        assert crud.get_document(db, document.id) is None

    finally:
        db.rollback()
        db.close()


def test_conversation_and_message_crud_operations():
    db = SessionLocal()
    username = unique_value("conversation_user")

    try:
        user = crud.create_user(db, username, "password_hash")

        conversation = crud.create_conversation(
            db, user.id, "Test conversation"
        )

        assert conversation.id is not None
        assert crud.get_conversation(db, conversation.id) is not None
        assert conversation in crud.list_conversations(db, user.id)

        message = crud.add_message(
            db,
            conversation.id,
            "user",
            "What is artificial intelligence?",
        )

        assert message.id is not None
        assert message.role == "user"

        messages = crud.list_messages(db, conversation.id)
        assert len(messages) == 1
        assert messages[0].content == "What is artificial intelligence?"

    finally:
        user = crud.get_user_by_username(db, username)
        if user:
            db.delete(user)
            db.commit()
        db.close()


def test_conversation_deletion_cascades_to_messages():
    db = SessionLocal()
    username = unique_value("cascade_user")

    try:
        user = crud.create_user(db, username, "password_hash")
        conversation = crud.create_conversation(
            db, user.id, "Cascade test"
        )

        message = crud.add_message(
            db,
            conversation.id,
            "user",
            "Test message",
        )

        message_id = message.id
        conversation_id = conversation.id

        assert crud.delete_conversation(db, conversation_id) is True

        db.expire_all()

        assert db.get(Message, message_id) is None
        assert crud.get_conversation(db, conversation_id) is None

    finally:
        user = crud.get_user_by_username(db, username)
        if user:
            db.delete(user)
            db.commit()
        db.close()


def test_user_deletion_cascades_to_conversations():
    db = SessionLocal()
    username = unique_value("user_cascade")

    try:
        user = crud.create_user(db, username, "password_hash")
        conversation = crud.create_conversation(
            db, user.id, "User cascade test"
        )

        conversation_id = conversation.id

        db.delete(user)
        db.commit()

        db.expire_all()

        assert db.get(Conversation, conversation_id) is None

    finally:
        user = crud.get_user_by_username(db, username)
        if user:
            db.delete(user)
            db.commit()
        db.close()


def test_database_indexes_exist():
    db = SessionLocal()

    try:
        inspector = inspect(db.bind)

        chunk_indexes = inspector.get_indexes("chunks")
        conversation_indexes = inspector.get_indexes("conversations")
        message_indexes = inspector.get_indexes("messages")

        assert any(
            index["name"] == "ix_chunks_embedding_hnsw"
            for index in chunk_indexes
        )

        assert any(
            index["name"] == "ix_conversations_user_id"
            for index in conversation_indexes
        )

        assert any(
            index["name"] == "ix_messages_conversation_id"
            for index in message_indexes
        )
    finally:
        db.close()
