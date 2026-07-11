import pandas as pd
import pytest

from echem_signal_toolkit.calibration import (
    calibration_performance_summary,
    estimate_loq,
    fit_replicate_calibration_curve,
    summarize_replicates,
)


def test_summarize_replicates_returns_mean_std_count_and_rsd():
    df = pd.DataFrame(
        {
            "concentration": [0, 0, 1, 1],
            "signal": [1.0, 3.0, 4.0, 6.0],
        }
    )

    summary = summarize_replicates(df)

    assert list(summary.columns) == [
        "concentration",
        "signal_mean",
        "signal_std",
        "signal_count",
        "signal_rsd_percent",
    ]

    blank = summary[summary["concentration"] == 0].iloc[0]
    one_um = summary[summary["concentration"] == 1].iloc[0]

    assert blank["signal_mean"] == pytest.approx(2.0)
    assert blank["signal_count"] == 2
    assert blank["signal_std"] == pytest.approx(1.41421356)
    assert blank["signal_rsd_percent"] == pytest.approx(70.710678, rel=1e-5)

    assert one_um["signal_mean"] == pytest.approx(5.0)


def test_summarize_replicates_single_replicate_has_zero_std():
    df = pd.DataFrame(
        {
            "concentration": [0, 1],
            "signal": [1.0, 2.0],
        }
    )

    summary = summarize_replicates(df)

    assert summary["signal_std"].tolist() == [0.0, 0.0]


def test_fit_replicate_calibration_curve_uses_mean_signal():
    replicate_summary = pd.DataFrame(
        {
            "concentration": [0, 1, 2],
            "signal_mean": [0.5, 2.5, 4.5],
            "signal_std": [0.1, 0.1, 0.1],
            "signal_count": [3, 3, 3],
            "signal_rsd_percent": [20.0, 4.0, 2.2],
        }
    )

    result = fit_replicate_calibration_curve(replicate_summary)

    assert result["slope"] == pytest.approx(2.0)
    assert result["intercept"] == pytest.approx(0.5)
    assert result["r_squared"] == pytest.approx(1.0)


def test_estimate_loq():
    blank_signals = [0.10, 0.12, 0.11, 0.09]

    loq = estimate_loq(blank_signals, slope=2.0)

    assert loq == pytest.approx(10.0 * pd.Series(blank_signals).std() / 2.0)


def test_calibration_performance_summary():
    fit_result = {
        "n_points": 4,
        "slope": 2.0,
        "intercept": 0.5,
        "r_squared": 0.99,
    }

    summary = calibration_performance_summary(
        fit_result=fit_result,
        lod=0.1,
        loq=0.3,
        concentration_unit="uM",
        signal_unit="uA",
    )

    assert summary["sensitivity"] == 2.0
    assert summary["sensitivity_unit"] == "uA/uM"
    assert summary["intercept"] == 0.5
    assert summary["r_squared"] == 0.99
    assert summary["lod"] == 0.1
    assert summary["loq"] == 0.3
    assert summary["n_points"] == 4