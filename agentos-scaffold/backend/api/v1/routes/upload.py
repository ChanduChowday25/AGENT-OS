"""
Upload controller.

Endpoints:
- POST /api/v1/upload
- DELETE /api/v1/files/{file_id}
"""

from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
)

from schemas.upload import UploadResponse
from services.file_service import (
    delete_uploaded_file,
    save_upload,
)


router = APIRouter()


# ================================================================
# Upload File
# ================================================================

@router.post(
    "/upload",
    response_model=UploadResponse,
)
async def upload_file(
    file: UploadFile,
):
    """
    Persist an uploaded file.
    """

    try:

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="Filename is required.",
            )

        content = await file.read()

        result = await save_upload(
            filename=file.filename,
            content=content,
        )

        return UploadResponse(
            file_id=result["file_id"],
            filename=result["filename"],
            status="uploaded",
        )

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ================================================================
# Delete File
# ================================================================

@router.delete(
    "/files/{file_id}",
)
async def delete_file(
    file_id: str,
):
    """
    Delete an uploaded file and its indexed document chunks.
    """

    try:

        result = delete_uploaded_file(
            file_reference=file_id,
        )

        return result

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail="Uploaded file not found.",
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )