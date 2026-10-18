"""Data models shared across the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PaperMeta:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: str = ""
    venue: str = ""  # conference / journal
    doi: str = ""
    arxiv_id: str = ""
    abstract: str = ""


@dataclass
class PaperSection:
    heading: str
    text: str
    level: int = 1  # 1=H1, 2=H2 ...


@dataclass
class PaperFigure:
    path: Path
    caption: str = ""
    page: int = 0
    figure_id: str = ""  # e.g. "fig1", "fig2"
    width: int = 0
    height: int = 0


@dataclass
class PaperContent:
    """Structured content extracted from a paper PDF."""

    meta: PaperMeta = field(default_factory=PaperMeta)
    full_text: str = ""
    sections: list[PaperSection] = field(default_factory=list)
    figures: list[PaperFigure] = field(default_factory=list)
    pdf_path: Optional[Path] = None
    num_pages: int = 0


@dataclass
class SlideData:
    """A single slide's content."""

    title: str
    bullets: list[str] = field(default_factory=list)
    notes: str = ""  # speaker notes
    figure_path: Optional[str] = None


@dataclass
class AnalyzedPaper:
    """LLM-analyzed paper content, ready for generators."""

    content: PaperContent = field(default_factory=PaperContent)
    summary_text: str = ""
    recommendation_score: int = 3  # 1-5
    recommendation_reason: str = ""
    slides: list[SlideData] = field(default_factory=list)
    script_text: str = ""
    notes_text: str = ""
    mindmap_markdown: str = ""
    poster_text: str = ""
    translated_summary: str = ""
