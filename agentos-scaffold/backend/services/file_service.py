"""
File service for AgentOS.

Responsibilities:
- Generate unique file IDs.
- Sanitize filenames.
- Persist uploaded files.
- Trigger document ingestion for documents.
- Save analytical files for the Analytics Agent.
- Resolve uploaded file references.
- Delete uploaded files and indexed document chunks.
- Return the saved file information.
"""

import re
import uuid
from pathlib import Path

from database.chroma_client import delete_documents_by_file_id
from services.document_ingestion_service import (
    document_ingestion_service,
)


# ================================================================
# Upload Directory
# ================================================================

UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ================================================================
# Supported File Types
# ================================================================

DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}

ANALYTICAL_EXTENSIONS = {
    ".csv",
    ".xls",
    ".xlsx",
}


# ================================================================
# Generate ID
# ================================================================

def generate_id() -> str:
    """
    Generate a unique identifier.
    """

    return str(uuid.uuid4())


# ================================================================
# Resolve File Path
# ================================================================

def resolve_file_path(
    file_reference: str,
) -> Path:
    """
    Resolve an uploaded file reference into its physical path.

    The reference can be:
    - a generated file ID
    - an existing file path

    Returns:
        Path to the uploaded file.
    """

    if not file_reference or not str(file_reference).strip():
        raise ValueError(
            "File reference cannot be empty."
        )

    file_reference = str(
        file_reference
    ).strip()

    # ------------------------------------------------------------
    # 1. If an actual path was already provided
    # ------------------------------------------------------------

    direct_path = Path(
        file_reference
    )

    if (
        direct_path.exists()
        and direct_path.is_file()
    ):
        return direct_path

    # ------------------------------------------------------------
    # 2. Treat the reference as a generated file ID
    # ------------------------------------------------------------

    matching_files = list(
        UPLOAD_DIR.glob(
            f"{file_reference}.*"
        )
    )

    if not matching_files:
        raise FileNotFoundError(
            f"Uploaded file not found for file reference: "
            f"{file_reference}"
        )

    return matching_files[0]


# ================================================================
# Delete Uploaded File
# ================================================================

def delete_uploaded_file(
    file_reference: str,
) -> dict:
    """
    Delete an uploaded file and its indexed document chunks.

    The reference can be:
    - a generated file ID
    - an existing file path

    Returns:
        Information about the deleted file.
    """

    file_path = resolve_file_path(
        file_reference
    )

    filename = file_path.name

    # ------------------------------------------------------------
    # Delete indexed document chunks from ChromaDB
    # ------------------------------------------------------------

    delete_documents_by_file_id(
        file_path.stem
    )

    # ------------------------------------------------------------
    # Delete physical file
    # ------------------------------------------------------------

    file_path.unlink()

    return {
        "filename": filename,
        "path": str(file_path),
        "status": "deleted",
    }


# ================================================================
# Safe Filename
# ================================================================

def safe_filename(
    filename: str,
) -> str:
    """
    Sanitize a user-provided filename.

    Prevents path traversal and removes unsafe characters.
    """

    if not filename:
        raise ValueError(
            "Filename cannot be empty."
        )

    name = Path(filename).name

    name = re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        name,
    )

    name = name.strip(".")

    if not name:
        raise ValueError(
            "Invalid filename."
        )

    return name


# ================================================================
# Save Uploaded File
# ================================================================

async def save_upload(
    filename: str,
    content: bytes,
) -> dict:
    """
    Save an uploaded file.

    Documents:
        PDF / DOCX / TXT
            ↓
        Document ingestion
            ↓
        ChromaDB

    Analytical files:
        CSV / XLS / XLSX
            ↓
        Save file
            ↓
        Analytics Agent processes it later
    """

    if not content:
        raise ValueError(
            "Uploaded file is empty."
        )

    clean_filename = safe_filename(
        filename
    )

    file_id = generate_id()

    # Keep the original extension.
    extension = Path(
        clean_filename
    ).suffix.lower()

    # ------------------------------------------------------------
    # Validate file type
    # ------------------------------------------------------------

    if (
        extension not in DOCUMENT_EXTENSIONS
        and extension not in ANALYTICAL_EXTENSIONS
    ):
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    file_path = (
        UPLOAD_DIR
        / f"{file_id}{extension}"
    )

    # ------------------------------------------------------------
    # 1. Save uploaded file
    # ------------------------------------------------------------

    file_path.write_bytes(
        content
    )

    try:

        # ========================================================
        # 2. DOCUMENT FILE
        # ========================================================

        if extension in DOCUMENT_EXTENSIONS:

            ingestion_result = (
                document_ingestion_service.ingest(
                    file_id=file_id,
                    file_path=str(file_path),
                )
            )

            return {
                "file_id": file_id,
                "filename": clean_filename,
                "path": str(file_path),
                "file_type": extension,
                "status": "indexed",
                "chunk_count": ingestion_result.get(
                    "chunk_count",
                    0,
                ),
                "embedding_dimension": ingestion_result.get(
                    "embedding_dimension",
                ),
            }

        # ========================================================
        # 3. ANALYTICAL FILE
        # ========================================================

        if extension in ANALYTICAL_EXTENSIONS:

            return {
                "file_id": file_id,
                "filename": clean_filename,
                "path": str(file_path),
                "file_type": extension,
                "status": "uploaded",
                "chunk_count": 0,
                "embedding_dimension": None,
            }

    except Exception:

        # If processing fails, remove the saved file.
        if file_path.exists():
            file_path.unlink()

        raise