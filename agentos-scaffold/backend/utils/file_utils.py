"""
Filesystem helpers shared by AgentOS services.
"""

import re
import uuid
from pathlib import Path


def generate_id() -> str:
    """
    Generate a unique identifier.
    """

    return str(uuid.uuid4())


def safe_filename(filename: str) -> str:
    """
    Sanitize a user-provided filename.

    Prevents path traversal and removes unsafe characters.
    """

    if not filename:
        raise ValueError("Filename cannot be empty.")

    name = Path(filename).name

    # Replace unsafe characters with underscores.
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)

    # Prevent hidden/empty filenames.
    name = name.strip(".")

    if not name:
        raise ValueError("Invalid filename.")

    return name