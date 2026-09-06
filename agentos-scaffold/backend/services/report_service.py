"""
Report Service for AgentOS.

Responsibilities:
- Save generated report metadata to SQLite.
- Retrieve all generated reports.
- Retrieve a specific report by report_id.

This service does NOT create PDF/DOCX files.
DocumentService handles file creation.
"""

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