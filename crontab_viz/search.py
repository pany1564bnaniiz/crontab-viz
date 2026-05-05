"""Search and filter cron expressions by description, tags, or schedule pattern."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from crontab_viz.parser import parse, ParseError
from crontab_viz.formatter import describe
from crontab_viz.tags import auto_tag


@dataclass
class SearchResult:
    expression: str
    description: str
    tags: List[str]
    score: float


def _tokenize(text: str) -> List[str]:
    """Return lowercase words from *text*."""
    return [w.strip().lower() for w in text.replace(",", " ").split() if w.strip()]


def _match_score(result: SearchResult, tokens: List[str]) -> float:
    """Return a relevance score (0.0 means no match)."""
    if not tokens:
        return 1.0

    haystack = " ".join(
        [result.expression.lower(), result.description.lower()] + [t.lower() for t in result.tags]
    )
    matched = sum(1 for tok in tokens if tok in haystack)
    return matched / len(tokens)


def search(
    expressions: List[str],
    query: str = "",
    tag_filter: Optional[str] = None,
    min_score: float = 0.5,
) -> List[SearchResult]:
    """Search *expressions* by *query* text and optional *tag_filter*.

    Returns results ordered by descending relevance score.
    """
    tokens = _tokenize(query)
    results: List[SearchResult] = []

    for expr in expressions:
        try:
            parsed = parse(expr)
        except ParseError:
            continue

        desc = describe(parsed)
        tagged = auto_tag(parsed)
        tags = tagged.tags

        if tag_filter and tag_filter.lower() not in [t.lower() for t in tags]:
            continue

        result = SearchResult(
            expression=expr,
            description=desc,
            tags=tags,
            score=0.0,
        )
        score = _match_score(result, tokens)
        if score >= min_score or not tokens:
            result.score = score
            results.append(result)

    results.sort(key=lambda r: r.score, reverse=True)
    return results


def format_results(results: List[SearchResult]) -> str:
    """Render *results* as a human-readable string."""
    if not results:
        return "No matching expressions found."

    lines = []
    for r in results:
        tag_str = ", ".join(r.tags) if r.tags else "none"
        lines.append(f"  {r.expression:<20}  {r.description}")
        lines.append(f"  {'':20}  tags: {tag_str}")
        lines.append("")
    return "\n".join(lines).rstrip()
