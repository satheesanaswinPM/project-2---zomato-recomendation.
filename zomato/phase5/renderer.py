"""Render display payloads as text, HTML, or JSON."""

from __future__ import annotations

import json

from phase5.models import DisplayPayload


def render_text(payload: DisplayPayload) -> str:
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append(payload.title.upper())
    lines.append("=" * 60)

    if payload.summary:
        lines.append(payload.summary)
    if payload.message:
        lines.append(payload.message)
    if payload.warnings:
        lines.append("Warnings: " + "; ".join(payload.warnings))

    if payload.is_empty:
        lines.append("")
        lines.append(payload.message or "No restaurants to display.")
        return "\n".join(lines)

    lines.append("")
    for item in payload.recommendations:
        lines.append(f"#{item.rank}  {item.name}")
        lines.append(
            f"    {item.location}  |  {item.cuisine}  |  "
            f"{item.cost_label}  |  Rating {item.rating_label}"
        )
        lines.append(f"    Why: {item.explanation}")
        lines.append("")

    return "\n".join(lines).rstrip()


def render_json(payload: DisplayPayload, *, indent: int = 2) -> str:
    return json.dumps(payload.to_dict(), indent=indent)


def render_html(payload: DisplayPayload) -> str:
    """Return an HTML fragment for embedding in templates."""
    parts: list[str] = []

    if payload.summary:
        parts.append(f'<p class="results-summary">{_escape(payload.summary)}</p>')

    if payload.message:
        css = "results-notice error" if payload.is_error else "results-notice"
        parts.append(f'<p class="{css}">{_escape(payload.message)}</p>')

    for warning in payload.warnings:
        parts.append(f'<p class="results-warning">{_escape(warning)}</p>')

    if payload.is_empty:
        parts.append('<div class="empty-state">')
        parts.append(f'<p>{_escape(payload.message or "No restaurants found.")}</p>')
        parts.append(
            "<p>Try lowering your minimum rating, changing cuisine, or adjusting budget.</p>"
        )
        parts.append("</div>")
        return "\n".join(parts)

    parts.append('<div class="results-list">')
    for item in payload.recommendations:
        parts.append('<article class="result-card">')
        parts.append(f'<div class="result-rank">#{item.rank}</div>')
        parts.append(f'<h3 class="result-name">{_escape(item.name)}</h3>')
        parts.append('<div class="result-meta">')
        parts.append(f'<span>{_escape(item.location)}</span>')
        parts.append(f'<span>{_escape(item.cuisine)}</span>')
        parts.append(f'<span>{_escape(item.cost_label)}</span>')
        parts.append(f'<span>Rating {item.rating_label}</span>')
        parts.append("</div>")
        parts.append(f'<p class="result-why"><strong>Why:</strong> {_escape(item.explanation)}</p>')
        parts.append("</article>")
    parts.append("</div>")
    return "\n".join(parts)


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
