"""Report export helpers for completed API jobs."""

import csv
import json
import re
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO, StringIO
from typing import Any, Literal
from zipfile import ZIP_DEFLATED, ZipFile

ExportFormat = Literal["json", "csv", "zip", "pdf", "chart.svg"]
ReportType = Literal["simulation", "comparison", "batch"]


class ExportNotAvailableError(ValueError):
    """Raised when a requested export cannot be built from a job result."""


class ExportService:
    """Build JSON, CSV, ZIP, PDF, and chart exports from job result payloads."""

    schema_version = 1

    def export(
        self,
        *,
        job_id: str,
        report_type: ReportType,
        result: Mapping[str, Any],
        export_format: ExportFormat,
    ) -> tuple[bytes, str, str]:
        document = self._document(job_id=job_id, report_type=report_type, result=result)
        filename_base = f"{report_type}-{job_id}"
        if export_format == "json":
            return (
                json.dumps(document, default=_json_default, indent=2).encode("utf-8"),
                "application/json",
                f"{filename_base}.json",
            )
        if export_format == "csv":
            return (
                self._primary_csv(report_type, result).encode("utf-8"),
                "text/csv; charset=utf-8",
                f"{filename_base}.csv",
            )
        if export_format == "zip":
            return (
                self._zip_bytes(document),
                "application/zip",
                f"{filename_base}.zip",
            )
        if export_format == "pdf":
            return (
                self._pdf_bytes(document),
                "application/pdf",
                f"{filename_base}.pdf",
            )
        if export_format == "chart.svg":
            return (
                self._chart_svg(report_type, document["report"]).encode("utf-8"),
                "image/svg+xml; charset=utf-8",
                f"{filename_base}-chart.svg",
            )
        raise ExportNotAvailableError(f"{export_format} export is not available")

    def _document(
        self,
        *,
        job_id: str,
        report_type: ReportType,
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        report = result.get("report")
        if not isinstance(report, Mapping):
            raise ExportNotAvailableError("report export is not available")
        metadata: dict[str, Any] = {
            "schema_version": self.schema_version,
            "job_id": job_id,
            "report_type": report_type,
            "generated_at": datetime.now(UTC).isoformat(),
        }
        if result.get("stop_reason") is not None:
            metadata["stop_reason"] = result["stop_reason"]
        return {
            "schema_version": self.schema_version,
            "metadata": metadata,
            "report": report,
        }

    def _primary_csv(self, report_type: ReportType, result: Mapping[str, Any]) -> str:
        payload = result.get("csv")
        if isinstance(payload, str):
            return payload
        report = result.get("report")
        if not isinstance(report, Mapping):
            raise ExportNotAvailableError("csv export is not available")
        if report_type == "simulation":
            return _rows_to_csv([_flatten_row(report)])
        return _rows_to_csv([_flatten_row(report)])

    def _zip_bytes(self, document: Mapping[str, Any]) -> bytes:
        output = BytesIO()
        report = document["report"]
        if not isinstance(report, Mapping):
            raise ExportNotAvailableError("zip export is not available")

        with ZipFile(output, "w", ZIP_DEFLATED) as archive:
            archive.writestr(
                "report.json",
                json.dumps(document, default=_json_default, indent=2).encode("utf-8"),
            )
            archive.writestr(
                "metadata.csv",
                _rows_to_csv([_flatten_row(document["metadata"])]),
            )
            archive.writestr("summary.csv", _rows_to_csv([_summary_row(report)]))
            for filename, rows in _detail_tables(report).items():
                archive.writestr(filename, _rows_to_csv(rows))
        return output.getvalue()

    def _pdf_bytes(self, document: Mapping[str, Any]) -> bytes:
        metadata = document["metadata"]
        report = document["report"]
        if not isinstance(metadata, Mapping) or not isinstance(report, Mapping):
            raise ExportNotAvailableError("pdf export is not available")

        lines = [
            "Blackjack Simulator Report",
            f"Type: {metadata.get('report_type', 'report')}",
            f"Job: {metadata.get('job_id', 'unknown')}",
            f"Generated: {metadata.get('generated_at', 'unknown')}",
            "",
            "Summary",
        ]
        lines.extend(f"{key}: {value}" for key, value in _summary_row(report).items())
        detail_tables = _detail_tables(report)
        for title, rows in detail_tables.items():
            lines.extend(["", title])
            for row in rows[:8]:
                lines.append(", ".join(f"{key}={value}" for key, value in row.items()))
        return _simple_pdf(lines)

    def _chart_svg(self, report_type: ReportType, report: Mapping[str, Any]) -> str:
        bars = _chart_bars(report_type, report)
        width = 720
        height = 320
        padding = 48
        chart_width = width - padding * 2
        chart_height = height - padding * 2
        max_value = max((abs(value) for _, value in bars), default=1) or 1
        bar_width = chart_width / max(len(bars), 1)
        elements = [
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
                f'height="{height}" viewBox="0 0 {width} {height}" role="img">'
            ),
            f"<title>{_xml_escape(report_type.title())} report chart</title>",
            '<rect width="100%" height="100%" fill="#f8fafc"/>',
            (
                f'<line x1="{padding}" y1="{height - padding}" '
                f'x2="{width - padding}" y2="{height - padding}" '
                'stroke="#64748b" stroke-width="1"/>'
            ),
        ]
        for index, (label, value) in enumerate(bars):
            x = padding + index * bar_width + 10
            bar_height = max(4, (abs(value) / max_value) * chart_height)
            y = height - padding - bar_height
            color = "#2563eb" if value >= 0 else "#dc2626"
            elements.append(
                (
                    f'<rect x="{x:.2f}" y="{y:.2f}" '
                    f'width="{max(12, bar_width - 20):.2f}" '
                    f'height="{bar_height:.2f}" fill="{color}" rx="3"/>'
                ),
            )
            elements.append(
                (
                    f'<text x="{x:.2f}" y="{height - 18}" '
                    'font-family="Arial" font-size="11" fill="#0f172a">'
                    f"{_xml_escape(label[:16])}</text>"
                ),
            )
            elements.append(
                (
                    f'<text x="{x:.2f}" y="{max(16, y - 6):.2f}" '
                    'font-family="Arial" font-size="11" fill="#0f172a">'
                    f"{value:g}</text>"
                ),
            )
        elements.append("</svg>")
        return "\n".join(elements)


def _summary_row(report: Mapping[str, Any]) -> dict[str, str]:
    ignored = {
        "results",
        "session_results",
        "percentile_final_bankrolls",
        "percentile_max_drawdowns",
    }
    row: dict[str, str] = {}
    for key, value in report.items():
        if key in ignored:
            continue
        if isinstance(value, Mapping):
            for nested_key, nested_value in value.items():
                if not isinstance(nested_value, list | dict):
                    row[f"{key}.{nested_key}"] = str(nested_value)
        elif not isinstance(value, list | dict):
            row[key] = str(value)
    return row


def _detail_tables(report: Mapping[str, Any]) -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    results = report.get("results")
    if isinstance(results, list):
        tables["comparison_results.csv"] = [
            _flatten_row(row) for row in results if isinstance(row, Mapping)
        ]
    sessions = report.get("session_results")
    if isinstance(sessions, list):
        tables["batch_sessions.csv"] = [
            _flatten_row(row) for row in sessions if isinstance(row, Mapping)
        ]
    final_percentiles = report.get("percentile_final_bankrolls")
    drawdown_percentiles = report.get("percentile_max_drawdowns")
    if isinstance(final_percentiles, Mapping) or isinstance(
        drawdown_percentiles,
        Mapping,
    ):
        final_keys = (
            final_percentiles.keys() if isinstance(final_percentiles, Mapping) else []
        )
        drawdown_keys = (
            drawdown_percentiles.keys()
            if isinstance(drawdown_percentiles, Mapping)
            else []
        )
        percentiles = sorted(
            {*final_keys, *drawdown_keys},
            key=str,
        )
        tables["batch_percentiles.csv"] = [
            {
                "percentile": str(percentile),
                "final_bankroll": str(final_percentiles.get(percentile, ""))
                if isinstance(final_percentiles, Mapping)
                else "",
                "max_drawdown": str(drawdown_percentiles.get(percentile, ""))
                if isinstance(drawdown_percentiles, Mapping)
                else "",
            }
            for percentile in percentiles
        ]
    return tables


def _chart_bars(
    report_type: ReportType,
    report: Mapping[str, Any],
) -> list[tuple[str, float]]:
    if report_type == "comparison":
        results = report.get("results")
        if isinstance(results, list):
            return [
                (
                    str(row.get("name", f"Config {index + 1}")),
                    _number(row.get("delta_net_result")),
                )
                for index, row in enumerate(results)
                if isinstance(row, Mapping)
            ]
    if report_type == "batch":
        percentiles = report.get("percentile_final_bankrolls")
        if isinstance(percentiles, Mapping):
            return [
                (f"p{key}", _number(value))
                for key, value in sorted(
                    percentiles.items(),
                    key=lambda item: str(item[0]),
                )
            ]
    return [
        ("Initial", _number(report.get("initial_bankroll"))),
        ("Final", _number(report.get("final_bankroll"))),
        ("Net", _number(report.get("net_result"))),
        ("Drawdown", _number(report.get("max_drawdown"))),
    ]


def _rows_to_csv(rows: Iterable[Mapping[str, Any]]) -> str:
    materialized = [dict(row) for row in rows]
    if not materialized:
        return ""
    fields: list[str] = []
    for row in materialized:
        for key in row:
            if key not in fields:
                fields.append(key)
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(materialized)
    return output.getvalue()


def _flatten_row(row: Mapping[str, Any], prefix: str = "") -> dict[str, str]:
    flattened: dict[str, str] = {}
    for key, value in row.items():
        field = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, Mapping):
            flattened.update(_flatten_row(value, field))
        elif isinstance(value, list):
            flattened[field] = json.dumps(value)
        else:
            flattened[field] = str(value)
    return flattened


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _json_default(value: Any) -> str:
    if isinstance(value, Decimal):
        return str(value)
    msg = f"object of type {type(value).__name__} is not JSON serializable"
    raise TypeError(msg)


def _simple_pdf(lines: Iterable[str]) -> bytes:
    width = 612
    height = 792
    x = 54
    y = 742
    leading = 16
    commands = ["BT", "/F1 11 Tf", f"{x} {y} Td"]
    first = True
    for raw_line in lines:
        for line in _wrap_pdf_line(str(raw_line)):
            if first:
                first = False
            else:
                commands.append(f"0 -{leading} Td")
                y -= leading
            if y < 54:
                commands.append(f"0 {742 - y} Td")
                y = 742
            commands.append(f"({_pdf_escape(line)}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 "
            + str(width).encode("ascii")
            + b" "
            + str(height).encode("ascii")
            + b"] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        (
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        ),
    ]
    output = BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(output.tell())
        output.write(f"{index} 0 obj\n".encode("ascii"))
        output.write(body)
        output.write(b"\nendobj\n")
    startxref = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.write(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{startxref}\n%%EOF\n"
        ).encode("ascii"),
    )
    return output.getvalue()


def _wrap_pdf_line(line: str, *, width: int = 86) -> list[str]:
    ascii_line = re.sub(r"[^\x20-\x7E]", "?", line)
    if len(ascii_line) <= width:
        return [ascii_line]
    chunks: list[str] = []
    current = ascii_line
    while len(current) > width:
        split_at = current.rfind(" ", 0, width)
        if split_at < 20:
            split_at = width
        chunks.append(current[:split_at])
        current = current[split_at:].lstrip()
    chunks.append(current)
    return chunks


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
