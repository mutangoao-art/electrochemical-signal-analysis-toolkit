from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


def smooth_current(
    df: pd.DataFrame,
    *,
    current_col: str = "current_a",
    output_col: str = "current_smoothed_a",
    window_length: int = 31,
    polyorder: int = 3,
) -> pd.DataFrame:
    """
    Smooth current data using a Savitzky-Golay filter.

    Parameters
    ----------
    df:
        Input dataframe.
    current_col:
        Name of the current column.
    output_col:
        Name of the smoothed current output column.
    window_length:
        Filter window length. Must be odd.
    polyorder:
        Polynomial order used by the filter.

    Returns
    -------
    pandas.DataFrame
        Dataframe with an added smoothed current column.
    """
    result = df.copy()

    if current_col not in result.columns:
        raise ValueError(f"Missing current column: {current_col}")

    current = result[current_col].to_numpy(dtype=float)
    window_length = _valid_window_length(window_length, current.size)

    if window_length <= polyorder:
        raise ValueError("window_length must be greater than polyorder")

    result[output_col] = savgol_filter(
        current,
        window_length=window_length,
        polyorder=polyorder,
    )

    return result


def baseline_correct_current(
    df: pd.DataFrame,
    *,
    potential_col: str = "potential_v",
    current_col: str = "current_a",
    output_col: str = "current_corrected_a",
    degree: int = 1,
    edge_fraction: float = 0.15,
) -> pd.DataFrame:
    """
    Correct baseline current using a polynomial fit to edge regions.

    This simple baseline correction estimates the background from the
    beginning and end portions of the voltammogram.

    Parameters
    ----------
    df:
        Input dataframe.
    potential_col:
        Name of the potential column.
    current_col:
        Name of the current column to correct.
    output_col:
        Name of the baseline-corrected current column.
    degree:
        Polynomial degree for baseline fitting.
    edge_fraction:
        Fraction of points from each edge used for baseline fitting.

    Returns
    -------
    pandas.DataFrame
        Dataframe with baseline and corrected current columns.
    """
    result = df.copy()

    _require_columns(result, [potential_col, current_col])

    if not 0 < edge_fraction < 0.5:
        raise ValueError("edge_fraction must be between 0 and 0.5")

    potential = result[potential_col].to_numpy(dtype=float)
    current = result[current_col].to_numpy(dtype=float)

    n_points = len(result)
    edge_points = max(int(n_points * edge_fraction), degree + 2)

    edge_indices = np.r_[
        0:edge_points,
        n_points - edge_points:n_points,
    ]

    baseline_coefficients = np.polyfit(
        potential[edge_indices],
        current[edge_indices],
        deg=degree,
    )

    baseline = np.polyval(baseline_coefficients, potential)

    result["baseline_a"] = baseline
    result[output_col] = current - baseline

    return result


def normalize_current(
    df: pd.DataFrame,
    *,
    current_col: str = "current_a",
    output_col: str = "current_normalized",
    method: str = "max_abs",
) -> pd.DataFrame:
    """
    Normalize current values.

    Supported methods:
    - max_abs: current divided by maximum absolute current
    - min_max: scaled to the range 0 to 1
    """
    result = df.copy()

    if current_col not in result.columns:
        raise ValueError(f"Missing current column: {current_col}")

    current = result[current_col].to_numpy(dtype=float)

    if method == "max_abs":
        denominator = np.nanmax(np.abs(current))

        if denominator == 0:
            raise ValueError("Cannot normalize current with maximum absolute value of zero")

        result[output_col] = current / denominator

    elif method == "min_max":
        current_min = np.nanmin(current)
        current_max = np.nanmax(current)
        denominator = current_max - current_min

        if denominator == 0:
            raise ValueError("Cannot min-max normalize constant current values")

        result[output_col] = (current - current_min) / denominator

    else:
        raise ValueError(f"Unsupported normalization method: {method}")

    return result


def _valid_window_length(window_length: int, data_length: int) -> int:
    if data_length < 3:
        raise ValueError("At least 3 data points are required for smoothing")

    window_length = min(window_length, data_length)

    if window_length % 2 == 0:
        window_length -= 1

    if window_length < 3:
        window_length = 3

    return window_length


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]

    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required column(s): {missing_text}")