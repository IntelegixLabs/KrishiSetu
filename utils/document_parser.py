import io
import os
import tempfile
from typing import List, Tuple

from fastapi import UploadFile

try:
    from markitdown import MarkItDown  # type: ignore
except Exception as e:  # pragma: no cover
    MarkItDown = None  # type: ignore


SUPPORTED_SUFFIXES = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".csv",
    ".txt",
    ".md",
}


def _guess_suffix(filename: str) -> str:
    filename_lower = (filename or "").lower()
    for ext in SUPPORTED_SUFFIXES:
        if filename_lower.endswith(ext):
            return ext
    return os.path.splitext(filename_lower)[1] or ".txt"


async def extract_texts_from_uploads(files: List[UploadFile]) -> List[Tuple[str, str]]:
    """Extract (filename, markdown_text) for each uploaded file using MarkItDown.

    Writes files to a temporary location to let MarkItDown handle various formats.
    Returns a list of (original_filename, extracted_markdown_text).
    """

    if not files:
        return []

    if MarkItDown is None:
        raise RuntimeError("markitdown is not installed. Please install markitdown[all].")

    md = MarkItDown()
    results: List[Tuple[str, str]] = []

    for f in files:
        try:
            suffix = _guess_suffix(f.filename or "")
            # Persist to a temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await f.read()
                tmp.write(content)
                tmp_path = tmp.name

            converted = md.convert(tmp_path)
            text = getattr(converted, "text_content", "") or ""
            results.append((f.filename or os.path.basename(tmp_path), text))
        except Exception as e:  # Continue processing other files
            results.append((f.filename or "unknown", f"[Extraction error] {e}"))
        finally:
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception:
                pass

    return results


