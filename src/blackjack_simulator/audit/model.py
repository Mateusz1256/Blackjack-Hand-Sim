"""Audit report data model."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class AuditStatus(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True, slots=True)
class AuditCheckResult:
    name: str
    status: AuditStatus
    description: str
    details: dict[str, Any] = field(default_factory=dict)
    violations: int = 0
    example_rounds: tuple[int, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "description": self.description,
            "details": self.details,
            "violations": self.violations,
            "example_rounds": list(self.example_rounds),
        }


@dataclass(frozen=True, slots=True)
class AuditReport:
    checks: tuple[AuditCheckResult, ...]

    @property
    def has_failures(self) -> bool:
        return any(check.status is AuditStatus.FAIL for check in self.checks)

    @property
    def has_warnings(self) -> bool:
        return any(check.status is AuditStatus.WARNING for check in self.checks)

    def exit_code(self, *, strict: bool = False) -> int:
        if self.has_failures:
            return 1
        if strict and self.has_warnings:
            return 1
        return 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": [check.to_dict() for check in self.checks],
            "summary": {
                "passed": sum(
                    check.status is AuditStatus.PASS for check in self.checks
                ),
                "warnings": sum(
                    check.status is AuditStatus.WARNING for check in self.checks
                ),
                "failed": sum(
                    check.status is AuditStatus.FAIL for check in self.checks
                ),
                "skipped": sum(
                    check.status is AuditStatus.SKIPPED for check in self.checks
                ),
            },
        }
