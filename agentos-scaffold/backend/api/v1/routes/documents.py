"""
Document Download Routes for AgentOS.

Responsibilities:
- Download generated PDF documents.
- Download generated DOCX documents.
- Validate document filenames.
- Prevent path traversal.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


router = APIRouter()


# ================================================================
# Generated document directory
# ================================================================

DOCUMENT_DIR = Path("generated_documents")

DOCUMENT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ================================================================
# Download Document
# ================================================================

@router.get(
    "/documents/{filename}",
    tags=["documents"],
)
async def download_document(
    filename: str,
):
    """
    Download a generated PDF or DOCX document.

    Example:

        GET /api/v1/documents/agentos_report.pdf

    The browser receives the actual file rather than
    the internal PDF/DOCX representation.
    """

    # ============================================================
    # Prevent path traversal
    # ============================================================

    safe_filename = Path(
        filename
    ).name

    if safe_filename != filename:

        raise HTTPException(
            status_code=400,
            detail="Invalid document filename.",
        )

    # ============================================================
    # Validate extension
    # ============================================================

    extension = (
        Path(safe_filename)
        .suffix
        .lower()
    )

    if extension not in {
        ".pdf",
        ".docx",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported document format. "
                "Only PDF and DOCX files are allowed."
            ),
        )

    # ============================================================
    # Build file path
    # ============================================================

    file_path = (
        DOCUMENT_DIR
        / safe_filename
    )

    # ============================================================
    # Check file exists
    # ============================================================

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                f"Document not found: "
                f"{safe_filename}"
            ),
        )

    if not file_path.is_file():

        raise HTTPException(
            status_code=404,
            detail="Requested document is not a file.",
        )

    # ============================================================
    # Determine media type
    # ============================================================

    if extension == ".pdf":

        media_type = "application/pdf"

    else:

        media_type = (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

    # ============================================================
    # Return actual file
    # ============================================================

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=safe_filename,
    )