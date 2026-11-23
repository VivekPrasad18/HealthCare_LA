"""
Text cleaning and section identification for scientific papers.
Input: raw page-by-page text from pdf_loader.
Output: section-labelled text blocks.
"""

from __future__ import annotations
import re
from typing import List, Tuple

from app.documents.pdf_loader import PageText

SectionBlock = Tuple[str, int, str]   # (section_label, page_no, text)

# Heuristic headings common in scientific papers (case-insensitive)
SECTION_PATTERNS = [
    (r"\babstract\b", "abstract"),
    (r"\bintroduction\b", "introduction"),
    (r"\brelated work\b|\bliterature review\b|\bbackground\b", "related_work"),
    (r"\bmethods?\b|\bmethodology\b|\bmaterials? and methods?\b", "methods"),
    (r"\bexperiments?\b|\bexperimental setup\b", "experiments"),
    (r"\bresults?\b", "results"),
    (r"\bdiscussion\b", "discussion"),
    (r"\bconclusions?\b", "conclusion"),
    (r"\blimitations?\b", "limitations"),
    (r"\breferences\b|\bbibliography\b", "references"),
]


def _clean_text(text: str) -> str:
    """Remove common PDF artefacts: excessive whitespace, hyphenation across lines."""
    # Join hyphenated line breaks
    text = re.sub(r"-\n", "", text)
    # Collapse multiple spaces / tabs
    text = re.sub(r"[ \t]+", " ", text)
    # Normalise newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _detect_section(line: str) -> str | None:
    """Return section label if the line looks like a section heading."""
    clean = line.strip().lower()
    # Headings are typically short (< 60 chars) and don't end with a period
    if len(clean) > 60 or clean.endswith("."):
        return None
    for pattern, label in SECTION_PATTERNS:
        if re.search(pattern, clean):
            return label
    return None


def parse_pages(pages: List[PageText]) -> List[SectionBlock]:
    """
    Walk page-by-page text, detect section boundaries, and return
    a list of (section_label, page_no, cleaned_text) blocks.
    """
    blocks: List[SectionBlock] = []
    current_section = "preamble"
    current_page = 1
    buffer: List[str] = []

    def flush():
        text = _clean_text("\n".join(buffer))
        if text:
            blocks.append((current_section, current_page, text))
        buffer.clear()

    for page_no, raw_text in pages:
        for line in raw_text.splitlines():
            detected = _detect_section(line)
            if detected:
                flush()
                current_section = detected
                current_page = page_no
            else:
                buffer.append(line)

    flush()
    return blocks


def extract_abstract_from_text(full_text: str) -> str | None:
    """
    Pull the abstract from raw full-text (fallback when PDF is unavailable
    and we only have concatenated text without page info).
    """
    match = re.search(
        r"\babstract\b(.+?)(?:\bintroduction\b|\bkeywords?\b|$)",
        full_text,
        re.IGNORECASE | re.DOTALL,
    )
    if match:
        return _clean_text(match.group(1))
    return None
