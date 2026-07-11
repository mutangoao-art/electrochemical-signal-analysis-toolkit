import pandas as pd
import pytest

from echem_signal_toolkit.batch import (
    analyze_cv_directory,
    analyze_cv_file,
    analyze_dpv_directory,
    analyze_dpv_file,
    save_batch_summary,
)
from echem_signal_toolkit.simulation import save_simulated_cv, save_simulated_dpv


def test_analyze_cv_file_returns_features(tmp_path):
    file_path = tmp_path / "sample.csv"
    save_simulated_cv(file_path, random_seed=1)

    result = analyze_cv_file(
        file_path,
        peak_prominence=0.5e-6,
        peak_distance=80,
    )

    assert result["sample_id"] == "sample"
    assert result["file_name"] == "sample.csv"
    assert result["n_points"] > 0
    assert "oxidation_peak_current_a" in result


def test_analyze_cv_file_uses_custom_sample_id(tmp_path):
    file_path = tmp_path / "sample.csv"
    save_simulated_cv(file_path, random_seed=1)

    result = analyze_cv_file(
        file_path,
        sample_id="custom_sample",
        peak_prominence=0.5e-6,
        peak_distance=80,
    )

    assert result["sample_id"] == "custom_sample"


def test_analyze_cv_directory_returns_summary(tmp_path):
    save_simulated_cv(tmp_path / "sample_a.csv", random_seed=1)
    save_simulated_cv(tmp_path / "sample_b.csv", random_seed=2)

    summary = analyze_cv_directory(
        tmp_path,
        pattern="*.csv",
        peak_prominence=0.5e-6,
        peak_distance=80,
    )

    assert len(summary) == 2
    assert set(summary["sample_id"]) == {"sample_a", "sample_b"}
    assert "oxidation_peak_current_a" in summary.columns


def test_analyze_cv_directory_rejects_empty_directory(tmp_path):
    with pytest.raises(ValueError, match="No files found"):
        analyze_cv_directory(tmp_path)


def test_save_batch_summary(tmp_path):
    summary = pd.DataFrame(
        {
            "sample_id": ["a", "b"],
            "oxidation_peak_current_a": [1e-6, 2e-6],
        }
    )

    output_path = tmp_path / "summary.csv"

    saved_path = save_batch_summary(summary, output_path)

    assert saved_path == output_path
    assert output_path.exists()

    loaded = pd.read_csv(output_path)

    assert loaded["sample_id"].tolist() == ["a", "b"]


def test_analyze_dpv_file_returns_features(tmp_path):
    file_path = tmp_path / "sample_dpv.csv"
    save_simulated_dpv(file_path, random_seed=1)

    result = analyze_dpv_file(
        file_path,
        peak_prominence=0.2e-6,
        peak_distance=60,
    )

    assert result["sample_id"] == "sample_dpv"
    assert result["file_name"] == "sample_dpv.csv"
    assert result["n_points"] > 0
    assert "peak_current_a" in result
    assert result["peak_current_a"] is not None


def test_analyze_dpv_file_uses_custom_sample_id(tmp_path):
    file_path = tmp_path / "sample_dpv.csv"
    save_simulated_dpv(file_path, random_seed=1)

    result = analyze_dpv_file(
        file_path,
        sample_id="custom_dpv_sample",
        peak_prominence=0.2e-6,
        peak_distance=60,
    )

    assert result["sample_id"] == "custom_dpv_sample"


def test_analyze_dpv_directory_returns_summary(tmp_path):
    save_simulated_dpv(tmp_path / "dpv_a.csv", random_seed=1)
    save_simulated_dpv(tmp_path / "dpv_b.csv", random_seed=2)

    summary = analyze_dpv_directory(
        tmp_path,
        pattern="*.csv",
        peak_prominence=0.2e-6,
        peak_distance=60,
    )

    assert len(summary) == 2
    assert set(summary["sample_id"]) == {"dpv_a", "dpv_b"}
    assert "peak_current_a" in summary.columns


def test_analyze_dpv_directory_rejects_empty_directory(tmp_path):
    with pytest.raises(ValueError, match="No files found"):
        analyze_dpv_directory(tmp_path)