from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from echem_signal_toolkit.io import read_chi_amperometry_data

def load_amperometry_data(file_path: str | Path) -> pd.DataFrame:
    """
    Load amperometry data from a standardized CSV or CHI i-t export file.
    """
    file_path = Path(file_path)

    if file_path.suffix.lower() == ".csv":
        return pd.read_csv(file_path)

    return read_chi_amperometry_data(file_path)

def analyze_amperometry_channel(
    df: pd.DataFrame,
    *,
    time_col: str = "time_s",
    current_col: str,
    baseline_window_s: tuple[float, float] | None = None,
    response_window_s: tuple[float, float] | None = None,
) -> dict[str, float | int | str | None]:
    """
    Analyze one amperometric current-time channel.

    If windows are not provided, the first 20% of points are used as baseline
    and the last 20% are used as steady-state response.
    """
    _require_columns(df, [time_col, current_col])

    clean = df[[time_col, current_col]].dropna().copy()

    if clean.empty:
        raise ValueError("No valid amperometry data points found")

    baseline_data = _select_window(
        clean,
        time_col=time_col,
        window=baseline_window_s,
        fallback="first",
    )

    response_data = _select_window(
        clean,
        time_col=time_col,
        window=response_window_s,
        fallback="last",
    )

    baseline_current = float(baseline_data[current_col].mean())
    steady_state_current = float(response_data[current_col].mean())
    response_current = steady_state_current - baseline_current

    noise_std = float(baseline_data[current_col].std(ddof=1))

    if np.isnan(noise_std):
        noise_std = 0.0

    snr = None
    if noise_std != 0:
        snr = float(abs(response_current) / noise_std)

    return {
        "channel": current_col.replace("_a", ""),
        "n_points": int(len(clean)),
        "time_min_s": float(clean[time_col].min()),
        "time_max_s": float(clean[time_col].max()),
        "baseline_current_a": baseline_current,
        "steady_state_current_a": steady_state_current,
        "response_current_a": float(response_current),
        "noise_std_a": noise_std,
        "snr": snr,
    }


def analyze_amperometry_file(
    file_path: str | Path,
    *,
    sample_id: str | None = None,
    channels: list[str] | None = None,
    baseline_window_s: tuple[float, float] | None = None,
    response_window_s: tuple[float, float] | None = None,
) -> pd.DataFrame:
    """
    Analyze all selected channels in one CHI amperometry file.
    """
    file_path = Path(file_path)
    df = load_amperometry_data(file_path)

    current_columns = [
        column for column in df.columns
        if column.startswith("i") and column.endswith("_a")
    ]

    if channels is not None:
        wanted = {f"{channel}_a" if not channel.endswith("_a") else channel for channel in channels}
        current_columns = [column for column in current_columns if column in wanted]

    if not current_columns:
        raise ValueError("No amperometry current channels found")

    rows = []

    for current_col in current_columns:
        result = analyze_amperometry_channel(
            df,
            current_col=current_col,
            baseline_window_s=baseline_window_s,
            response_window_s=response_window_s,
        )

        rows.append(
            {
                "sample_id": sample_id or file_path.stem,
                "file_name": file_path.name,
                **result,
            }
        )

    return pd.DataFrame(rows)


def analyze_amperometry_directory(
    directory: str | Path,
    *,
    pattern: str = "*.txt",
    channels: list[str] | None = None,
    baseline_window_s: tuple[float, float] | None = None,
    response_window_s: tuple[float, float] | None = None,
) -> pd.DataFrame:
    """
    Analyze CHI amperometry files in a directory.
    """
    directory = Path(directory)
    file_paths = sorted(directory.glob(pattern))

    if not file_paths:
        raise ValueError(f"No files found in {directory} matching pattern {pattern}")

    summaries = [
        analyze_amperometry_file(
            file_path,
            channels=channels,
            baseline_window_s=baseline_window_s,
            response_window_s=response_window_s,
        )
        for file_path in file_paths
    ]

    return pd.concat(summaries, ignore_index=True)


def _select_window(
    df: pd.DataFrame,
    *,
    time_col: str,
    window: tuple[float, float] | None,
    fallback: str,
) -> pd.DataFrame:
    if window is not None:
        start_s, end_s = window
        selected = df[(df[time_col] >= start_s) & (df[time_col] <= end_s)]

        if selected.empty:
            raise ValueError(f"No data points found in window {window}")

        return selected

    n_points = len(df)
    window_points = max(int(n_points * 0.2), 1)

    if fallback == "first":
        return df.iloc[:window_points]

    if fallback == "last":
        return df.iloc[-window_points:]

    raise ValueError("fallback must be 'first' or 'last'")


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]

    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required column(s): {missing_text}")