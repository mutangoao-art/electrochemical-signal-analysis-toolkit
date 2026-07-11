from __future__ import annotations

import pandas as pd

from echem_signal_toolkit.features import features_to_dataframe
from echem_signal_toolkit.peaks import detect_peaks, get_main_peak
from echem_signal_toolkit.preprocessing import baseline_correct_current, smooth_current


def analyze_dpv(
    df: pd.DataFrame,
    *,
    potential_col: str = "potential_v",
    current_col: str = "current_a",
    smoothing_window: int = 21,
    smoothing_polyorder: int = 3,
    baseline_degree: int = 1,
    baseline_edge_fraction: float = 0.15,
    peak_prominence: float | None = None,
    peak_distance: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float | int | None]]:
    """
    Analyze differential pulse voltammetry data.

    Returns:
    - processed dataframe
    - detected peak table
    - extracted DPV feature dictionary
    """
    processed = smooth_current(
        df,
        current_col=current_col,
        output_col="current_smoothed_a",
        window_length=smoothing_window,
        polyorder=smoothing_polyorder,
    )

    processed = baseline_correct_current(
        processed,
        potential_col=potential_col,
        current_col="current_smoothed_a",
        output_col="current_corrected_a",
        degree=baseline_degree,
        edge_fraction=baseline_edge_fraction,
    )

    peaks = detect_peaks(
        processed,
        potential_col=potential_col,
        current_col="current_corrected_a",
        prominence=peak_prominence,
        distance=peak_distance,
        peak_type="oxidation",
    )

    features = extract_dpv_features(
        processed,
        peaks,
        potential_col=potential_col,
        current_col="current_corrected_a",
    )

    return processed, peaks, features


def extract_dpv_features(
    df: pd.DataFrame,
    peaks: pd.DataFrame,
    *,
    potential_col: str = "potential_v",
    current_col: str = "current_a",
) -> dict[str, float | int | None]:
    """
    Extract DPV peak features.

    DPV is commonly used for quantitative biosensing, so the main feature is
    the oxidation peak current and its peak potential.
    """
    _require_columns(df, [potential_col, current_col])

    features: dict[str, float | int | None] = {
        "n_points": int(len(df)),
        "n_detected_peaks": int(len(peaks)),
        "potential_min_v": float(df[potential_col].min()),
        "potential_max_v": float(df[potential_col].max()),
        "current_min_a": float(df[current_col].min()),
        "current_max_a": float(df[current_col].max()),
        "current_range_a": float(df[current_col].max() - df[current_col].min()),
    }

    if peaks.empty:
        features["peak_potential_v"] = None
        features["peak_current_a"] = None
        features["peak_prominence_a"] = None
        return features

    main_peak = get_main_peak(peaks, peak_type="oxidation")

    features["peak_potential_v"] = float(main_peak["potential_v"])
    features["peak_current_a"] = float(main_peak["current_a"])

    if "prominence_a" in main_peak:
        features["peak_prominence_a"] = float(main_peak["prominence_a"])
    else:
        features["peak_prominence_a"] = None

    return features


def dpv_features_to_dataframe(features: dict[str, float | int | None]) -> pd.DataFrame:
    """
    Convert DPV features to a dataframe.
    """
    return features_to_dataframe(features)


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]

    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required column(s): {missing_text}")