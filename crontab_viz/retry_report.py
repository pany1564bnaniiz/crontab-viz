"""Generate a structured retry-policy report for one or more expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .retry import RetryAnalysis, analyze_retry


@dataclass
class RetryReportEntry:
    expression: str
    analysis: RetryAnalysis

    @property
    def status(self) -> str:
        if not self.analysis.ok:
            return "error"
        return "conflict" if self.analysis.has_conflicts else "ok"


@dataclass
class RetryReport:
    entries: List[RetryReportEntry] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def conflict_count(self) -> int:
        return sum(1 for e in self.entries if e.status == "conflict")

    @property
    def error_count(self) -> int:
        return sum(1 for e in self.entries if e.status == "error")

    def summary(self) -> str:
        lines = [
            f"Retry Report — {self.generated_at:%Y-%m-%d %H:%M} UTC",
            f"Expressions checked : {self.total}",
            f"Conflicts detected  : {self.conflict_count}",
            f"Errors              : {self.error_count}",
            "",
        ]
        for entry in self.entries:
            marker = {"ok": "✓", "conflict": "⚠", "error": "✗"}.get(entry.status, "?")
            lines.append(f"  {marker} {entry.expression}")
            if entry.status != "ok":
                for line in entry.analysis.summary().splitlines()[1:]:
                    lines.append(f"      {line}")
        return "\n".join(lines)


def generate_report(
    expressions: List[str],
    retry_interval_minutes: int = 5,
    max_retries: int = 3,
    window: int = 24,
    now: Optional[datetime] = None,
) -> RetryReport:
    """Build a RetryReport for a list of cron expressions."""
    report = RetryReport(generated_at=now or datetime.utcnow())
    for expr in expressions:
        analysis = analyze_retry(
            expression=expr,
            retry_interval_minutes=retry_interval_minutes,
            max_retries=max_retries,
            window=window,
            now=now,
        )
        report.entries.append(RetryReportEntry(expression=expr, analysis=analysis))
    return report
