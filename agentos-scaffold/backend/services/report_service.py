"""
Report Service for AgentOS.

Responsibilities:
- Save generated report metadata to SQLite.
- Retrieve all generated reports.
- Retrieve a specific report by report_id.
- Delete generated report metadata and the physical file.

This service does NOT create PDF/DOCX files.
DocumentService handles file creation.
"""

import os
import uuid

from database.connection import SessionLocal
from models.generated_report import GeneratedReport


# ================================================================
# Create Report
# ================================================================

def create_report(
    filename: str,
    report_format: str,
    storage_path: str,
) -> dict:
    """
    Save metadata for a newly generated report.
    """

    report_id = str(uuid.uuid4())

    db = SessionLocal()

    try:

        report = GeneratedReport(
            id=report_id,
            filename=filename,
            format=report_format,
            storage_path=storage_path,
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        return {
            "report_id": report.id,
            "filename": report.filename,
            "format": report.format,
            "storage_path": report.storage_path,
            "created_at": (
                report.created_at.isoformat()
                if report.created_at
                else None
            ),
        }

    finally:

        db.close()


# ================================================================
# Get All Reports
# ================================================================

def get_reports() -> list:
    """
    Return all generated report metadata.
    """

    db = SessionLocal()

    try:

        reports = (
            db.query(GeneratedReport)
            .order_by(
                GeneratedReport.created_at.desc()
            )
            .all()
        )

        return [
            {
                "report_id": report.id,
                "filename": report.filename,
                "format": report.format,
                "created_at": (
                    report.created_at.isoformat()
                    if report.created_at
                    else None
                ),
            }
            for report in reports
        ]

    finally:

        db.close()


# ================================================================
# Get Report By ID
# ================================================================

def get_report_by_id(
    report_id: str,
):
    """
    Return a generated report by its ID.
    """

    db = SessionLocal()

    try:

        report = (
            db.query(GeneratedReport)
            .filter(
                GeneratedReport.id == report_id
            )
            .first()
        )

        if not report:
            return None

        return {
            "report_id": report.id,
            "filename": report.filename,
            "format": report.format,
            "storage_path": report.storage_path,
            "created_at": (
                report.created_at.isoformat()
                if report.created_at
                else None
            ),
        }

    finally:

        db.close()


# ================================================================
# Delete Report
# ================================================================

def delete_report(
    report_id: str,
) -> bool:
    """
    Delete a generated report.

    This removes:
    1. The physical PDF/DOCX file.
    2. The corresponding SQLite metadata record.

    Returns:
        True  -> report was deleted.
        False -> report was not found.
    """

    db = SessionLocal()

    try:

        report = (
            db.query(GeneratedReport)
            .filter(
                GeneratedReport.id == report_id
            )
            .first()
        )

        if not report:
            return False

        storage_path = report.storage_path

        # --------------------------------------------------------
        # Delete physical file first.
        # --------------------------------------------------------

        if storage_path:

            try:

                if os.path.isfile(storage_path):

                    os.remove(storage_path)

            except OSError as exc:

                raise RuntimeError(
                    f"Unable to delete report file: {exc}"
                ) from exc

        # --------------------------------------------------------
        # Delete database record.
        # --------------------------------------------------------

        db.delete(report)
        db.commit()

        return True

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()