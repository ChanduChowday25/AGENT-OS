"""Report routes for AgentOS."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from schemas.report import ReportListResponse
from services.report_service import (
    get_reports,
    get_report_by_id,
    delete_report,
)


router = APIRouter()


# ================================================================
# List Reports
# ================================================================

@router.get(
    "/reports",
    response_model=ReportListResponse,
)
async def list_reports():
    """Return all generated reports."""

    reports = get_reports()

    return {
        "reports": reports
    }


# ================================================================
# Download Report
# ================================================================

@router.get(
    "/reports/{report_id}/download",
    tags=["reports"],
)
async def download_report(
    report_id: str,
):
    """Download a generated PDF or DOCX report using report_id."""

    report = get_report_by_id(report_id)

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    file_path = Path(report["storage_path"])

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Report file not found.",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Report path is not a file.",
        )

    if report["format"].lower() == "pdf":

        media_type = "application/pdf"

    elif report["format"].lower() == "docx":

        media_type = (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

    else:

        raise HTTPException(
            status_code=400,
            detail="Unsupported report format.",
        )

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=report["filename"],
    )


# ================================================================
# Delete Report
# ================================================================

@router.delete(
    "/reports/{report_id}",
    tags=["reports"],
)
async def delete_report_route(
    report_id: str,
):
    """
    Delete a generated report and its physical PDF/DOCX file.
    """

    try:

        deleted = delete_report(
            report_id
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to delete the report.",
        )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    return {
        "report_id": report_id,
        "message": "Report deleted successfully.",
    }