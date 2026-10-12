"""Extract plain text from PDF and transcript files for use with add_material.

OWNER: Mano (@Mkkumar2006) — Stretch goal, issue #8.

Usage (from server.py or a CLI):
    from ingest import extract_text
    text = extract_text("lecture.pdf")

Supports:
- .pdf  — via PyMuPDF (fitz); falls back to pdfminer.six if fitz is absent
- .txt / .md / .rst / .csv and any other plain-text formats
- .vtt  — WebVTT transcript (strips timestamps/cue headers)
- .srt  — SubRip transcript (strips indices and timestamps)

Raises FileNotFoundError if the file does not exist.
Raises ValueError for unsupported binary formats.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _strip_vtt(raw: str) -> str:
    """Remove WebVTT headers, cue timings, and NOTE blocks; keep spoken text."""
    lines = []
    skip_next = False
    for line in raw.splitlines():
        stripped = line.strip()
        # skip WEBVTT header and NOTE blocks
        if stripped.startswith("WEBVTT") or stripped.startswith("NOTE"):
            skip_next = True
            continue
        # skip timestamp lines like "00:00:01.000 --> 00:00:04.000"
        if re.match(r"^\d{2}:\d{2}[\d:.]+\s*-->\s*\d{2}:\d{2}", stripped):
            skip_next = False
            continue
        if skip_next and not stripped:
            skip_next = False
            continue
        if stripped:
            lines.append(stripped)
    return "\n".join(lines)


def _strip_srt(raw: str) -> str:
    """Remove SRT indices and timestamp lines; keep subtitle text."""
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.isdigit():
            continue
        if re.match(r"^\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}", stripped):
            continue
        if stripped:
            lines.append(stripped)
    return "\n".join(lines)


def _extract_pdf(path: Path) -> str:
    """Extract text from a PDF using PyMuPDF, falling back to pdfminer.six."""
    # try PyMuPDF first (faster, better layout)
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(path))
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(pages)
    except ImportError:
        pass

    # fall back to pdfminer.six
    try:
        from pdfminer.high_level import extract_text as pm_extract

        return pm_extract(str(path))
    except ImportError:
        raise ImportError(
            "No PDF library found. Install one:\n"
            "  pip install pymupdf          # recommended\n"
            "  pip install pdfminer.six     # alternative"
        )


def extract_text(file_path: str | Path) -> str:
    """Return the plain-text content of *file_path*.

    Parameters
    ----------
    file_path:
        Path to a .pdf, .vtt, .srt, or plain-text file.

    Returns
    -------
    str
        Extracted text, ready to pass to ``generate.make_cards`` or
        ``server.add_material``.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the format is not supported.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(path)

    if suffix == ".vtt":
        return _strip_vtt(_read_text(path))

    if suffix == ".srt":
        return _strip_srt(_read_text(path))

    # treat everything else as UTF-8 text (includes .txt, .md, .rst, .csv …)
    # reject obvious binary formats
    binary_suffixes = {
        ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls",
        ".odt", ".jpg", ".jpeg", ".png", ".gif", ".mp3", ".mp4",
        ".zip", ".gz", ".tar",
    }
    if suffix in binary_suffixes:
        raise ValueError(
            f"Unsupported file format: {suffix}. "
            "Supported formats: .pdf, .txt, .md, .rst, .csv, .vtt, .srt"
        )

    return _read_text(path)


# ── CLI helper ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <file>", file=sys.stderr)
        sys.exit(1)
    print(extract_text(sys.argv[1]))
