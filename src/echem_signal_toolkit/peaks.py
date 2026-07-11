from __future__ import annotations

import pandas as pd
from scipy.signal import find_peaks


def detect_peaks(
    df: pd.DataFrame,
    *,
    potential_col: str = "potential_v",
    current_col: str = "current_a",
    prominence: float | None = None,
    distance: int | None = None,
    peak_type: str = "oxidation",
) -> pd.DataFrame:
    """
    Detect oxidation or reduction peaks in CV data.

    Parameters
    ----------
    df:
        Input dataframe.
    potential_col:
        Name of the potential column.
    current_col:
        Name of the current column.
    prominence:
        Required peak prominence. If None, scipy chooses no fixed threshold.
    distance:
        Required minimum horizontal distance between peaks, in points.
    peak_type:
        oxidation for positive peaks, reduction for negative peaks.

    Returns
    -------
    pandas.DataFrame
        Peak table with peak index, potential, current, and peak type.
    """
    _require_columns(df, [potential_col, current_col])

    current = df[current_col].to_numpy(dtype=float)

    if peak_type == "oxidation":
        signal = current
    elif peak_type == "reduction":
        signal = -current
    else:
        raise ValueError("peak_type must be 'oxidation' or 'reduction'")

    peak_indices, properties = find_peaks(
        signal,
        prominence=prominence,
        distance=distance,
    )

    peaks = pd.DataFrame(
        {
            "peak_index": peak_indices,
            "potential_v": df.iloc[peak_indices][potential_col].to_numpy(),
            "current_a": df.iloc[peak_indices][current_col].to_numpy(),
            "peak_type": peak_type,
        }
    )

    if "prominences" in properties:
        peaks["prominence_a"] = properties["prominences"]

    return peaks.reset_index(drop=True)


def detect_cv_peaks(
    df: pd.DataFrame,
    *,
    potential_col: str = "potential_v",
    current_col: str = "current_a",
    prominence: float | None = None,
    distance: int | None = None,
) -> pd.DataFrame:
    """
    Detect both oxidation and reduction peaks in CV data.
    """
    oxidation_peaks = detect_peaks(
        df,
        potential_col=potential_col,
        current_col=current_col,
        prominence=prominence,
        distance=distance,
        peak_type="oxidation",
    )

    reduction_peaks = detect_peaks(
        df,
        potential_col=potential_col,
        current_col=current_col,
        prominence=prominence,
        distance=distance,
        peak_type="reduction",
    )

    return pd.concat([oxidation_peaks, reduction_peaks], ignore_index=True)


def get_main_peak(
    peaks: pd.DataFrame,
    *,
    peak_type: str = "oxidation",
) -> pd.Series:
    """
    Return the most intense peak of the requested type.
    """
    selected = peaks[peaks["peak_type"] == peak_type]

    if selected.empty:
        raise ValueError(f"No {peak_type} peak found")

    if peak_type == "oxidation":
        peak_position = selected["current_a"].idxmax()
    elif peak_type == "reduction":
        peak_position = selected["current_a"].idxmin()
    else:
        raise ValueError("peak_type must be 'oxidation' or 'reduction'")

    return selected.loc[peak_position]


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]

    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required column(s): {missing_text}")