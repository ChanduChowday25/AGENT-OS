"""
ChromaDB client wrapper for document embeddings.

Rule: embeddings live only here, never in SQLite.
"""

import chromadb

from config.settings import get_settings


settings = get_settings()

_client = None


def get_chroma_client():
    global _client

    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR
        )

    return _client


def get_document_collection():
    """Return the document_embeddings collection."""
    client = get_chroma_client()

    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME
    )


def delete_documents_by_file_id(file_id: str):
    """
    Delete all indexed document chunks belonging to a file.
    """

    if not file_id or not file_id.strip():
        raise ValueError(
            "File ID cannot be empty."
        )

    collection = get_document_collection()

    collection.delete(
        where={
            "file_id": file_id.strip()
        }
    )