import pandas as pd

from echem_signal_toolkit.report import (
    generate_calibration_report,
    generate_markdown_report,
)


def test_generate_markdown_report(tmp_path):
    output_path = tmp_path / "cv_report.md"

    features = {
        "oxidation_peak_potential_v": 0.45,
        "oxidation_peak_current_a": 5e-6,
    }

    peaks = pd.DataFrame(
        {
            "peak_type": ["oxidation"],
            "potential_v": [0.45],
            "current_a": [5e-6],
            "prominence_a": [1e-6],
        }
    )

    saved_path = generate_markdown_report(
        output_path=output_path,
        title="Test CV Report",
        features=features,
        peaks=peaks,
        notes="Test note.",
    )

    assert saved_path == output_path
    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")

    assert "# Test CV Report" in content
    assert "`oxidation_peak_potential_v`" in content
    assert "Detected Peaks" in content
    assert "Test note." in content


def test_generate_calibration_report(tmp_path):
    output_path = tmp_path / "calibration_report.md"

    performance = {
        "sensitivity": 0.2,
        "sensitivity_unit": "uA/uM",
        "r_squared": 0.99,
        "lod": 0.1,
        "loq": 0.3,
    }

    replicate_summary = pd.DataFrame(
        {
            "concentration": [0.0, 1.0],
            "signal_mean": [0.1, 0.3],
            "signal_std": [0.01, 0.02],
            "signal_count": [3, 3],
            "signal_rsd_percent": [10.0, 6.67],
        }
    )

    saved_path = generate_calibration_report(
        output_path=output_path,
        title="Test Calibration Report",
        performance=performance,
        replicate_summary=replicate_summary,
        notes="Calibration note.",
    )

    assert saved_path == output_path
    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")

    assert "# Test Calibration Report" in content
    assert "Calibration Performance" in content
    assert "`sensitivity`" in content
    assert "Replicate Summary" in content
    assert "Calibration note." in content