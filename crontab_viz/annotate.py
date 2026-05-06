"""Annotate cron expressions with inline human-readable comments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .parser import parse, ParseError
from .formatter import describe
from .validator import validate
from .lint import lint


@dataclass
class AnnotatedExpression:
    expression: str
    description: str
    warnings: list[str]
    suggestions: list[str]
    is_valid: bool

    def inline_comment(self, style: str = "#") -> str:
        """Return the expression with a trailing inline comment."""
        return f"{self.expression}  {style} {self.description}"

    def full_report(self) -> str:
        """Return a multi-line annotation block."""
        lines = [
            f"Expression : {self.expression}",
            f"Description: {self.description}",
        ]
        if self.warnings:
            for w in self.warnings:
                lines.append(f"Warning    : {w}")
        if self.suggestions:
            for s in self.suggestions:
                lines.append(f"Suggestion : {s}")
        if not self.is_valid:
            lines.append("Status     : INVALID")
        return "\n".join(lines)


def annotate(expression: str) -> AnnotatedExpression:
    """Parse and annotate a single cron expression."""
    val = validate(expression)
    if not val:
        return AnnotatedExpression(
            expression=expression,
            description="(invalid expression)",
            warnings=list(val.errors),
            suggestions=[],
            is_valid=False,
        )

    try:
        cron = parse(expression)
        desc = describe(cron)
    except ParseError as exc:  # pragma: no cover
        return AnnotatedExpression(
            expression=expression,
            description="(parse error)",
            warnings=[str(exc)],
            suggestions=[],
            is_valid=False,
        )

    lint_result = lint(cron)
    warnings = list(val.warnings) + lint_result.warnings
    suggestions = lint_result.suggestions

    return AnnotatedExpression(
        expression=expression,
        description=desc,
        warnings=warnings,
        suggestions=suggestions,
        is_valid=True,
    )


def annotate_many(expressions: list[str]) -> list[AnnotatedExpression]:
    """Annotate a list of cron expressions."""
    return [annotate(expr) for expr in expressions]
