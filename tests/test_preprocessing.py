import pandas as pd

from echem_signal_toolkit.preprocessing import (
    baseline_correct_current,
    normalize_current,
    smooth_current,
)


def test_smooth_current_adds_output_column():
    df = pd.DataFrame(
        {
            "potential_v": [0.0, 0.1, 0.2, 0.3, 0.4],
            "current_a": [1e-6, 2e-6, 1.5e-6, 2.5e-6, 2e-6],
        }
    )

    result = smooth_current(df, window_length=5, polyorder=2)

    assert "current_smoothed_a" in result.columns
    assert len(result) == len(df)


def test_baseline_correct_current_adds_columns():
    df = pd.DataFrame(
        {
            "potential_v": [0.0, 0.1, 0.2, 0.3, 0.4],
            "current_a": [1e-6, 1.1e-6, 1.2e-6, 1.3e-6, 1.4e-6],
        }
    )

    result = baseline_correct_current(df, degree=1, edge_fraction=0.2)

    assert "baseline_a" in result.columns
    assert "current_corrected_a" in result.columns


def test_normalize_current_max_abs():
    df = pd.DataFrame({"current_a": [-2.0, 0.0, 1.0]})

    result = normalize_current(df)

    assert result["current_normalized"].tolist() == [-1.0, 0.0, 0.5]