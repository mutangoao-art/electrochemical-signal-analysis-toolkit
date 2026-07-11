import pandas as pd

from echem_signal_toolkit.features import extract_cv_features, features_to_dataframe


def test_extract_cv_features_returns_expected_keys():
    df = pd.DataFrame(
        {
            "potential_v": [0.0, 0.1, 0.2, 0.3],
            "current_a": [0.0, 1e-6, -0.5e-6, 0.0],
        }
    )

    peaks = pd.DataFrame(
        {
            "potential_v": [0.1, 0.2],
            "current_a": [1e-6, -0.5e-6],
            "peak_type": ["oxidation", "reduction"],
        }
    )

    features = extract_cv_features(df, peaks)

    assert features["n_points"] == 4
    assert features["n_detected_peaks"] == 2
    assert features["oxidation_peak_potential_v"] == 0.1
    assert features["reduction_peak_potential_v"] == 0.2
    assert features["peak_separation_v"] == -0.1


def test_features_to_dataframe_has_feature_and_value_columns():
    features = {
        "oxidation_peak_potential_v": 0.1,
        "oxidation_peak_current_a": 1e-6,
    }

    table = features_to_dataframe(features)

    assert list(table.columns) == ["feature", "value"]
    assert len(table) == 2