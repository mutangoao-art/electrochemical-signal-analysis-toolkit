from __future__ import annotations

from pathlib import Path

import pandas as pd


def generate_markdown_report(
    *,
    output_path: str | Path,
    title: str,
    features: dict[str, float | int | None],
    peaks: pd.DataFrame,
    plot_path: str | Path | None = None,
    notes: str | None = None,
) -> Path:
    """
    Generate a Markdown report for an electrochemical analysis result.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        f"# {title}",
        "",
        "## Summary",
        "",
        "| Feature | Value |",
        "|---|---:|",
    ]

    for key, value in features.items():
        lines.append(f"| `{key}` | {_format_value(value)} |")

    lines.extend(
        [
            "",
            "## Detected Peaks",
            "",
        ]
    )

    if peaks.empty:
        lines.append("No peaks detected.")
    else:
        lines.extend(_peaks_to_markdown_lines(peaks))

    if plot_path is not None:
        plot_path = Path(plot_path)
        lines.extend(
            [
                "",
                "## Plot",
                "",
                f"![CV analysis plot]({plot_path.as_posix()})",
            ]
        )

    if notes:
        lines.extend(
            [
                "",
                "## Notes",
                "",
                notes,
            ]
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return output_path


def _peaks_to_markdown_lines(peaks: pd.DataFrame) -> list[str]:
    display = peaks.copy()

    if "current_a" in display.columns:
        display["current_uA"] = display["current_a"] * 1e6

    columns = [
        column
        for column in ["peak_type", "potential_v", "current_uA", "prominence_a"]
        if column in display.columns
    ]

    lines = [
        "| Peak Type | Potential (V) | Current (uA) | Prominence (A) |",
        "|---|---:|---:|---:|",
    ]

    for _, row in display[columns].iterrows():
        lines.append(
            "| "
            f"{row.get('peak_type', '')} | "
            f"{_format_value(row.get('potential_v'))} | "
            f"{_format_value(row.get('current_uA'))} | "
            f"{_format_value(row.get('prominence_a'))} |"
        )

    return lines


def _format_value(value: object) -> str:
    if value is None:
        return "N/A"

    if isinstance(value, float):
        return f"{value:.6g}"

    return str(value)