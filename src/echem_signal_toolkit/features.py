from __future__ import annotations

import numpy as np
import pandas as pd


def extract_cv_features(
    df: pd.DataFrame,
    peaks: pd.DataFrame,
    *,
    potential_col: str = "potential_v",
    current_col: str = "current_a",
) -> dict[str, float | int | None]:
    """
    Extract summary features from cyclic voltammetry data.

    Returned features include:
    - oxidation peak potential and current
    - reduction peak potential and current
    - peak separation
    - oxidation/reduction current ratio
    - current range
    - integrated absolute charge-like area

    Notes
    -----
    The integrated area is calculated as absolute current integrated over
    potential. It is useful as a shape descriptor, not as a formal charge
    unless scan rate and time-domain details are handled explicitly.
    """
    _require_columns(df, [potential_col, current_col])
    _require_columns(peaks, ["potential_v", "current_a", "peak_type"])

    oxidation_peak = _main_peak(peaks, peak_type="oxidation")
    reduction_peak = _main_peak(peaks, peak_type="reduction")

    features: dict[str, float | int | None] = {
        "n_points": int(len(df)),
        "n_detected_peaks": int(len(peaks)),
        "potential_min_v": float(df[potential_col].min()),
        "potential_max_v": float(df[potential_col].max()),
        "current_min_a": float(df[current_col].min()),
        "current_max_a": float(df[current_col].max()),
        "current_range_a": float(df[current_col].max() - df[current_col].min()),
        "integrated_abs_current_av": float(
            np.trapezoid(
                np.abs(df[current_col].to_numpy(dtype=float)),
                df[potential_col].to_numpy(dtype=float),
            )
        ),
    }

    if oxidation_peak is not None:
        features["oxidation_peak_potential_v"] = float(oxidation_peak["potential_v"])
        features["oxidation_peak_current_a"] = float(oxidation_peak["current_a"])
    else:
        features["oxidation_peak_potential_v"] = None
        features["oxidation_peak_current_a"] = None

    if reduction_peak is not None:
        features["reduction_peak_potential_v"] = float(reduction_peak["potential_v"])
        features["reduction_peak_current_a"] = float(reduction_peak["current_a"])
    else:
        features["reduction_peak_potential_v"] = None
        features["reduction_peak_current_a"] = None

    if oxidation_peak is not None and reduction_peak is not None:
        features["peak_separation_v"] = float(
            oxidation_peak["potential_v"] - reduction_peak["potential_v"]
        )

        reduction_current = float(reduction_peak["current_a"])

        if reduction_current != 0:
            features["oxidation_reduction_current_ratio_abs"] = float(
                abs(oxidation_peak["current_a"]) / abs(reduction_current)
            )
        else:
            features["oxidation_reduction_current_ratio_abs"] = None
    else:
        features["peak_separation_v"] = None
        features["oxidation_reduction_current_ratio_abs"] = None

    return features


def features_to_dataframe(features: dict[str, float | int | None]) -> pd.DataFrame:
    """
    Convert a feature dictionary to a two-column dataframe.
    """
    return pd.DataFrame(
        {
            "feature": list(features.keys()),
            "value": list(features.values()),
        }
    )


def _main_peak(
    peaks: pd.DataFrame,
    *,
    peak_type: str,
) -> pd.Series | None:
    selected = peaks[peaks["peak_type"] == peak_type]

    if selected.empty:
        return None

    if peak_type == "oxidation":
        return selected.loc[selected["current_a"].idxmax()]

    if peak_type == "reduction":
        return selected.loc[selected["current_a"].idxmin()]

    raise ValueError("peak_type must be 'oxidation' or 'reduction'")


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]

    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required column(s): {missing_text}")