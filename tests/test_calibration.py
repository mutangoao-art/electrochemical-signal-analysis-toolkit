import numpy as np
import pandas as pd
import pytest

from echem_signal_toolkit.calibration import (
    build_calibration_table,
    calibration_from_batch_summary,
    estimate_lod,
    estimate_lod_from_batch_summary,
    fit_calibration_curve,
    predict_signal,
)

def test_build_calibration_table():
    concentrations = [0, 1, 2]
    signals = [0.1, 0.3, 0.5]

    table = build_calibration_table(concentrations, signals)

    assert list(table.columns) == ["concentration", "signal"]
    assert table["concentration"].tolist() == concentrations
    assert table["signal"].tolist() == signals


def test_build_calibration_table_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        build_calibration_table([0, 1], [0.1])


def test_fit_calibration_curve_returns_expected_linear_fit():
    calibration = pd.DataFrame(
        {
            "concentration": [0, 1, 2, 3],
            "signal": [0.5, 2.5, 4.5, 6.5],
        }
    )

    result = fit_calibration_curve(calibration)

    assert result["n_points"] == 4
    assert result["slope"] == pytest.approx(2.0)
    assert result["intercept"] == pytest.approx(0.5)
    assert result["r_squared"] == pytest.approx(1.0)


def test_predict_signal_with_scalar():
    predicted = predict_signal(2.0, slope=3.0, intercept=1.0)

    assert predicted == pytest.approx(7.0)


def test_predict_signal_with_array():
    concentrations = np.array([0.0, 1.0, 2.0])

    predicted = predict_signal(concentrations, slope=2.0, intercept=0.5)

    assert predicted.tolist() == pytest.approx([0.5, 2.5, 4.5])


def test_estimate_lod():
    blank_signals = np.array([0.10, 0.12, 0.11, 0.09])

    lod = estimate_lod(blank_signals, slope=2.0, multiplier=3.0)

    expected = 3.0 * np.std(blank_signals, ddof=1) / 2.0

    assert lod == pytest.approx(expected)


def test_estimate_lod_rejects_zero_slope():
    with pytest.raises(ValueError, match="Slope must be non-zero"):
        estimate_lod([0.1, 0.2, 0.3], slope=0.0)

def test_calibration_from_batch_summary():
    summary = pd.DataFrame(
        {
            "sample_id": ["blank_1", "sample_1uM", "sample_5uM"],
            "oxidation_peak_current_a": [0.1e-6, 1.0e-6, 5.0e-6],
        }
    )

    concentration_map = {
        "blank_1": 0.0,
        "sample_1uM": 1.0,
        "sample_5uM": 5.0,
    }

    calibration = calibration_from_batch_summary(
        summary,
        concentration_map=concentration_map,
    )

    assert calibration["sample_id"].tolist() == ["blank_1", "sample_1uM", "sample_5uM"]
    assert calibration["concentration"].tolist() == [0.0, 1.0, 5.0]
    assert calibration["signal"].tolist() == [0.1e-6, 1.0e-6, 5.0e-6]


def test_calibration_from_batch_summary_skips_unmapped_samples():
    summary = pd.DataFrame(
        {
            "sample_id": ["blank_1", "unknown_sample", "sample_1uM"],
            "oxidation_peak_current_a": [0.1e-6, 999e-6, 1.0e-6],
        }
    )

    concentration_map = {
        "blank_1": 0.0,
        "sample_1uM": 1.0,
    }

    calibration = calibration_from_batch_summary(
        summary,
        concentration_map=concentration_map,
    )

    assert calibration["sample_id"].tolist() == ["blank_1", "sample_1uM"]


def test_calibration_from_batch_summary_rejects_no_matches():
    summary = pd.DataFrame(
        {
            "sample_id": ["unknown_sample"],
            "oxidation_peak_current_a": [1.0e-6],
        }
    )

    with pytest.raises(ValueError, match="No summary rows matched"):
        calibration_from_batch_summary(
            summary,
            concentration_map={"sample_1uM": 1.0},
        )


def test_estimate_lod_from_batch_summary():
    summary = pd.DataFrame(
        {
            "sample_id": ["blank_1", "blank_2", "blank_3", "sample_1uM", "sample_2uM"],
            "oxidation_peak_current_a": [0.10, 0.12, 0.11, 1.10, 2.10],
        }
    )

    concentration_map = {
        "blank_1": 0.0,
        "blank_2": 0.0,
        "blank_3": 0.0,
        "sample_1uM": 1.0,
        "sample_2uM": 2.0,
    }

    lod = estimate_lod_from_batch_summary(
        summary,
        concentration_map=concentration_map,
        blank_sample_ids=["blank_1", "blank_2", "blank_3"],
    )

    assert lod > 0


def test_estimate_lod_from_batch_summary_requires_multiple_blanks():
    summary = pd.DataFrame(
        {
            "sample_id": ["blank_1", "sample_1uM", "sample_2uM"],
            "oxidation_peak_current_a": [0.10, 1.10, 2.10],
        }
    )

    concentration_map = {
        "blank_1": 0.0,
        "sample_1uM": 1.0,
        "sample_2uM": 2.0,
    }

    with pytest.raises(ValueError, match="At least two blank rows"):
        estimate_lod_from_batch_summary(
            summary,
            concentration_map=concentration_map,
            blank_sample_ids=["blank_1"],
        )