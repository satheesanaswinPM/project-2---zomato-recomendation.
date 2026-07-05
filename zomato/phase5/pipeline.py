"""Present recommendation responses in the chosen output format."""

from __future__ import annotations

from typing import Literal

from phase4.models import RecommendationResponse
from phase5.models import DisplayPayload
from phase5.parser import parse_response
from phase5.renderer import render_html, render_json, render_text

OutputFormat = Literal["text", "html", "json"]


def present(
    response: RecommendationResponse,
    *,
    output_format: OutputFormat = "text",
) -> str | DisplayPayload:
    """
    Parse and render a recommendation response.

    Returns raw string for text/html/json formats, or DisplayPayload if needed
  by callers for templates.
    """
    payload = parse_response(response)

    if output_format == "json":
        return render_json(payload)
    if output_format == "html":
        return render_html(payload)
    return render_text(payload)


def build_display_payload(response: RecommendationResponse) -> DisplayPayload:
    return parse_response(response)
