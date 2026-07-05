"""Phase 5 — Output Display: parse and render recommendations."""

from phase5.models import DisplayPayload, DisplayRecommendation
from phase5.parser import parse_response
from phase5.pipeline import present
from phase5.renderer import render_html, render_json, render_text

__all__ = [
    "DisplayPayload",
    "DisplayRecommendation",
    "parse_response",
    "present",
    "render_html",
    "render_json",
    "render_text",
]
