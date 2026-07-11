import pandas as pd

from echem_signal_toolkit.peaks import detect_cv_peaks, get_main_peak


def test_detect_cv_peaks_finds_oxidation_and_reduction():
    df = pd.DataFrame(
        {
            "potential_v": [0.0, 0.1, 0.2, 0.3, 0.4],
            "current_a": [0.0, 1.0, 0.0, -1.0, 0.0],
        }
    )

    peaks = detect_cv_peaks(df, prominence=0.5)

    assert "oxidation" in peaks["peak_type"].tolist()
    assert "reduction" in peaks["peak_type"].tolist()


def test_get_main_peak_returns_expected_peak():
    peaks = pd.DataFrame(
        {
            "potential_v": [0.2, 0.4],
            "current_a": [1e-6, 3e-6],
            "peak_type": ["oxidation", "oxidation"],
        }
    )

    main_peak = get_main_peak(peaks, peak_type="oxidation")

    assert main_peak["potential_v"] == 0.4
    assert main_peak["current_a"] == 3e-6