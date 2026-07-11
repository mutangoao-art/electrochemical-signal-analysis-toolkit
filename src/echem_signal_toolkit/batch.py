from __future__ import annotations

from pathlib import Path

import pandas as pd

from echem_signal_toolkit.features import extract_cv_features
from echem_signal_toolkit.io import load_cv_data
from echem_signal_toolkit.peaks import detect_cv_peaks
from echem_signal_toolkit.preprocessing import baseline_correct_current, smooth_current
from echem_signal_toolkit.dpv import analyze_dpv


def analyze_cv_file(
    file_path: str | Path,
    *,
    sample_id: str | None = None,
    current_unit: str = "A",
    smoothing_window: int = 31,
    smoothing_polyorder: int = 3,
    baseline_degree: int = 1,
    baseline_edge_fraction: float = 0.15,
    peak_prominence: float | None = None,
    peak_distance: int | None = None,
) -> dict[str, object]:
    """
    Analyze a single CV file and return extracted features.

    The workflow is:
    load data -> smooth current -> baseline correction -> peak detection
    -> feature extraction.
    """
    file_path = Path(file_path)

    cv_data = load_cv_data(
        file_path,
        current_unit=current_unit,
    )

    processed = smooth_current(
        cv_data,
        current_col="current_a",
        output_col="current_smoothed_a",
        window_length=smoothing_window,
        polyorder=smoothing_polyorder,
    )

    processed = baseline_correct_current(
        processed,
        potential_col="potential_v",
        current_col="current_smoothed_a",
        output_col="current_corrected_a",
        degree=baseline_degree,
        edge_fraction=baseline_edge_fraction,
    )

    peaks = detect_cv_peaks(
        processed,
        potential_col="potential_v",
        current_col="current_corrected_a",
        prominence=peak_prominence,
        distance=peak_distance,
    )

    features = extract_cv_features(
        processed,
        peaks,
        potential_col="potential_v",
        current_col="current_corrected_a",
    )

    result: dict[str, object] = {
        "sample_id": sample_id or file_path.stem,
        "file_name": file_path.name,
        **features,
    }

    return result


def analyze_cv_directory(
    directory: str | Path,
    *,
    pattern: str = "*.csv",
    current_unit: str = "A",
    peak_prominence: float | None = None,
    peak_distance: int | None = None,
) -> pd.DataFrame:
    """
    Analyze all CV files in a directory and return a feature summary table.
    """
    directory = Path(directory)
    file_paths = sorted(directory.glob(pattern))

    if not file_paths:
        raise ValueError(f"No files found in {directory} matching pattern {pattern}")

    results = [
        analyze_cv_file(
            file_path,
            current_unit=current_unit,
            peak_prominence=peak_prominence,
            peak_distance=peak_distance,
        )
        for file_path in file_paths
    ]

    return pd.DataFrame(results)

def analyze_dpv_file(
    file_path: str | Path,
    *,
    sample_id: str | None = None,
    current_unit: str = "A",
    peak_prominence: float | None = None,
    peak_distance: int | None = None,
) -> dict[str, object]:
    """
    Analyze a single DPV file and return extracted features.
    """
    file_path = Path(file_path)

    dpv_data = load_cv_data(
        file_path,
        current_unit=current_unit,
    )

    _, _, features = analyze_dpv(
        dpv_data,
        peak_prominence=peak_prominence,
        peak_distance=peak_distance,
    )

    return {
        "sample_id": sample_id or file_path.stem,
        "file_name": file_path.name,
        **features,
    }


def analyze_dpv_directory(
    directory: str | Path,
    *,
    pattern: str = "*.csv",
    current_unit: str = "A",
    peak_prominence: float | None = None,
    peak_distance: int | None = None,
) -> pd.DataFrame:
    """
    Analyze all DPV files in a directory and return a feature summary table.
    """
    directory = Path(directory)
    file_paths = sorted(directory.glob(pattern))

    if not file_paths:
        raise ValueError(f"No files found in {directory} matching pattern {pattern}")

    results = [
        analyze_dpv_file(
            file_path,
            current_unit=current_unit,
            peak_prominence=peak_prominence,
            peak_distance=peak_distance,
        )
        for file_path in file_paths
    ]

    return pd.DataFrame(results)

def save_batch_summary(
    summary: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """
    Save batch analysis summary table to CSV.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary.to_csv(output_path, index=False)

    return output_path