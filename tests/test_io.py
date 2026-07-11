import pandas as pd

from echem_signal_toolkit.io import standardize_cv_dataframe


def test_standardize_cv_dataframe_with_standard_columns():
    raw = pd.DataFrame(
        {
            "Potential (V)": [0.0, 0.1, 0.2],
            "Current (uA)": [1.0, 2.0, 3.0],
        }
    )

    standardized = standardize_cv_dataframe(
        raw,
        potential_col="Potential (V)",
        current_col="Current (uA)",
        current_unit="uA",
    )

    assert list(standardized.columns) == ["potential_v", "current_a"]
    assert standardized["potential_v"].tolist() == [0.0, 0.1, 0.2]
    assert standardized["current_a"].tolist() == [1e-6, 2e-6, 3e-6]


def test_standardize_cv_dataframe_with_time_and_cycle():
    raw = pd.DataFrame(
        {
            "E/V": [0.0, 0.1],
            "I/A": [1e-6, 2e-6],
            "Time (s)": [0.0, 1.0],
            "Cycle": [1, 1],
        }
    )

    standardized = standardize_cv_dataframe(raw)

    assert list(standardized.columns) == [
        "potential_v",
        "current_a",
        "time_s",
        "cycle",
    ]
    assert standardized["cycle"].tolist() == [1, 1]