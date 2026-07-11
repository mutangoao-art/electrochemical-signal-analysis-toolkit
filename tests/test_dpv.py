import pandas as pd

from echem_signal_toolkit.dpv import (
    analyze_dpv,
    dpv_features_to_dataframe,
    extract_dpv_features,
)
from echem_signal_toolkit.simulation import generate_simulated_dpv


def test_generate_simulated_dpv_has_expected_columns():
    df = generate_simulated_dpv(n_points=100, random_seed=1)

    assert list(df.columns) == ["potential_v", "current_a"]
    assert len(df) == 100


def test_analyze_dpv_returns_processed_peaks_and_features():
    df = generate_simulated_dpv(n_points=300, random_seed=1)

    processed, peaks, features = analyze_dpv(
        df,
        peak_prominence=0.5e-6,
        peak_distance=50,
    )

    assert "current_smoothed_a" in processed.columns
    assert "current_corrected_a" in processed.columns
    assert len(peaks) >= 1
    assert features["n_points"] == 300
    assert features["peak_current_a"] is not None
    assert features["peak_potential_v"] is not None


def test_extract_dpv_features_with_peak():
    df = pd.DataFrame(
        {
            "potential_v": [0.0, 0.1, 0.2],
            "current_a": [0.0, 1.0e-6, 0.0],
        }
    )

    peaks = pd.DataFrame(
        {
            "peak_index": [1],
            "potential_v": [0.1],
            "current_a": [1.0e-6],
            "peak_type": ["oxidation"],
            "prominence_a": [0.8e-6],
        }
    )

    features = extract_dpv_features(df, peaks)

    assert features["n_points"] == 3
    assert features["n_detected_peaks"] == 1
    assert features["peak_potential_v"] == 0.1
    assert features["peak_current_a"] == 1.0e-6
    assert features["peak_prominence_a"] == 0.8e-6


def test_extract_dpv_features_without_peak():
    df = pd.DataFrame(
        {
            "potential_v": [0.0, 0.1, 0.2],
            "current_a": [0.0, 0.1e-6, 0.0],
        }
    )

    peaks = pd.DataFrame(
        columns=["peak_index", "potential_v", "current_a", "peak_type"]
    )

    features = extract_dpv_features(df, peaks)

    assert features["n_detected_peaks"] == 0
    assert features["peak_potential_v"] is None
    assert features["peak_current_a"] is None
    assert features["peak_prominence_a"] is None


def test_dpv_features_to_dataframe():
    features = {
        "peak_potential_v": 0.1,
        "peak_current_a": 1e-6,
    }

    table = dpv_features_to_dataframe(features)

    assert list(table.columns) == ["feature", "value"]
    assert len(table) == 2