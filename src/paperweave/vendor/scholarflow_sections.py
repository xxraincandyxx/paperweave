"""ScholarFlow section detection, MIT, cc66f783. Kept as the compatibility layer."""
import re
from .scholarflow_models import PaperSection
SECTION_HEADINGS = [
    "abstract", "introduction", "related work", "background",
    "method", "methodology", "approach", "model", "architecture",
    "experiment", "experiments", "results", "evaluation",
    "discussion", "analysis", "ablation",
    "conclusion", "conclusions", "future work",
    "acknowledgment", "acknowledgments", "acknowledgements",
    "references", "appendix",
]

_HEADING_RE = re.compile(
    r"^(?:\d+\.?\s*)?(" + "|".join(SECTION_HEADINGS) + r")\b",
    re.IGNORECASE,
)

def _detect_sections(text: str) -> list[PaperSection]:
    sections: list[PaperSection] = []
    lines = text.split("\n")
    current_heading = "Preamble"
    current_text: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_text.append("")
            continue

        m = _HEADING_RE.match(stripped)
        if m and len(stripped) < 80:
            if current_text:
                sections.append(
                    PaperSection(heading=current_heading, text="\n".join(current_text).strip())
                )
            current_heading = stripped
            current_text = []
        else:
            current_text.append(stripped)

    if current_text:
        sections.append(
            PaperSection(heading=current_heading, text="\n".join(current_text).strip())
        )
    return sections

HEADING_RE = _HEADING_RE
detect_sections = _detect_sections


def _guess_title_from_text(text: str) -> str:
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    skip_patterns = [
        r"(?i)(provided|permission|copyright|licensed|arxiv|preprint|submitted|accepted)",
        r"(?i)(reproduce|distribution|granted|journal|work\b)",
        r"^https?://",
        r"^[\d\s\-/.,@]+$",
        r"@[a-zA-Z]",
    ]
    for line in lines[:20]:
        if len(line) < 8:
            continue
        if any(re.search(p, line) for p in skip_patterns):
            continue
        if not re.search(r"[A-Z]", line):
            continue
        return line
    return lines[0] if lines else "Untitled Paper"

guess_title_from_text = _guess_title_from_text
