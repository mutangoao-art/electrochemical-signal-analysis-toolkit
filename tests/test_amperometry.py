import pandas as pd
import pytest

from echem_signal_toolkit.amperometry import (
    analyze_amperometry_channel,
    analyze_amperometry_directory,
    analyze_amperometry_file,
)
from echem_signal_toolkit.simulation import save_simulated_amperometry


def test_analyze_amperometry_channel_returns_expected_features():
    df = pd.DataFrame(
        {
            "time_s": [1, 2, 3, 4, 5],
            "i4_a": [1e-9, 1e-9, 2e-9, 3e-9, 3e-9],
        }
    )

    result = analyze_amperometry_channel(
        df,
        current_col="i4_a",
        baseline_window_s=(1, 2),
        response_window_s=(4, 5),
    )

    assert result["channel"] == "i4"
    assert result["n_points"] == 5
    assert result["baseline_current_a"] == pytest.approx(1e-9)
    assert result["steady_state_current_a"] == pytest.approx(3e-9)
    assert result["response_current_a"] == pytest.approx(2e-9)


def test_analyze_amperometry_channel_uses_default_windows():
    df = pd.DataFrame(
        {
            "time_s": list(range(1, 11)),
            "i4_a": [1e-9, 1e-9, 1e-9, 1e-9, 2e-9, 2e-9, 3e-9, 3e-9, 3e-9, 3e-9],
        }
    )

    result = analyze_amperometry_channel(df, current_col="i4_a")

    assert result["baseline_current_a"] == pytest.approx(1e-9)
    assert result["steady_state_current_a"] == pytest.approx(3e-9)


def test_analyze_amperometry_channel_rejects_empty_window():
    df = pd.DataFrame(
        {
            "time_s": [1, 2, 3],
            "i4_a": [1e-9, 2e-9, 3e-9],
        }
    )

    with pytest.raises(ValueError, match="No data points found in window"):
        analyze_amperometry_channel(
            df,
            current_col="i4_a",
            baseline_window_s=(10, 20),
        )


def test_analyze_amperometry_file_returns_channel_summary(tmp_path):
    file_path = tmp_path / "simulated_amperometry.csv"
    save_simulated_amperometry(file_path, channels=["i4", "i6"], random_seed=1)

    summary = analyze_amperometry_file(
        file_path,
        channels=["i4"],
        baseline_window_s=(0, 15),
        response_window_s=(80, 100),
    )

    assert len(summary) == 1
    assert summary.iloc[0]["sample_id"] == "simulated_amperometry"
    assert summary.iloc[0]["file_name"] == "simulated_amperometry.csv"
    assert summary.iloc[0]["channel"] == "i4"
    assert "response_current_a" in summary.columns


def test_analyze_amperometry_directory_returns_summary(tmp_path):
    save_simulated_amperometry(tmp_path / "sample_a.csv", random_seed=1)
    save_simulated_amperometry(tmp_path / "sample_b.csv", random_seed=2)

    summary = analyze_amperometry_directory(
        tmp_path,
        pattern="*.csv",
        channels=["i4"],
        baseline_window_s=(0, 15),
        response_window_s=(80, 100),
    )

    assert len(summary) == 2
    assert set(summary["sample_id"]) == {"sample_a", "sample_b"}
    assert set(summary["channel"]) == {"i4"}


def test_analyze_amperometry_directory_rejects_empty_directory(tmp_path):
    with pytest.raises(ValueError, match="No files found"):
        analyze_amperometry_directory(tmp_path)