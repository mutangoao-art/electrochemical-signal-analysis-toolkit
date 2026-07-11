from __future__ import annotations

from pathlib import Path

import pandas as pd

from echem_signal_toolkit.io import load_cv_data
from echem_signal_toolkit.peaks import detect_cv_peaks, get_main_peak
from echem_signal_toolkit.plotting import plot_cv, plot_cv_with_peaks, save_plot
from echem_signal_toolkit.preprocessing import baseline_correct_current, smooth_current
from echem_signal_toolkit.simulation import save_simulated_cv
from echem_signal_toolkit.features import extract_cv_features, features_to_dataframe
from echem_signal_toolkit.report import generate_markdown_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "simulated_cv.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_cv_processed.csv"
PEAK_TABLE_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_cv_peaks.csv"

RAW_PLOT_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_cv_raw.png"
PROCESSED_PLOT_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_cv_processed_peaks.png"
FEATURE_TABLE_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_cv_features.csv"
REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_cv_report.md"


def main() -> None:
    print("Generating simulated CV data...")
    save_simulated_cv(RAW_DATA_PATH)

    print("Loading CV data...")
    cv_data = load_cv_data(RAW_DATA_PATH)

    print("Smoothing current signal...")
    processed = smooth_current(
        cv_data,
        current_col="current_a",
        output_col="current_smoothed_a",
        window_length=31,
        polyorder=3,
    )

    print("Applying baseline correction...")
    processed = baseline_correct_current(
        processed,
        potential_col="potential_v",
        current_col="current_smoothed_a",
        output_col="current_corrected_a",
        degree=1,
        edge_fraction=0.15,
    )

    print("Detecting CV peaks...")
    peaks = detect_cv_peaks(
        processed,
        potential_col="potential_v",
        current_col="current_corrected_a",
        prominence=0.5e-6,
        distance=80,
    )
    print("Extracting CV features...")
    features = extract_cv_features(
        processed,
        peaks,
        potential_col="potential_v",
        current_col="current_corrected_a",
    )

    feature_table = features_to_dataframe(features)

    oxidation_peak = get_main_peak(peaks, peak_type="oxidation")
    reduction_peak = get_main_peak(peaks, peak_type="reduction")

    print("\nMain oxidation peak:")
    print(_format_peak(oxidation_peak))

    print("\nMain reduction peak:")
    print(_format_peak(reduction_peak))

    print("\nSaving processed data and peak table...")
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    processed.to_csv(PROCESSED_DATA_PATH, index=False)
    peaks.to_csv(PEAK_TABLE_PATH, index=False)

    feature_table.to_csv(FEATURE_TABLE_PATH, index=False)

    print("Saving plots...")
    plot_cv(
        cv_data,
        potential_col="potential_v",
        current_col="current_a",
        title="Simulated CV Raw Signal",
        current_unit="uA",
    )
    save_plot(RAW_PLOT_PATH)

    plot_cv_with_peaks(
        processed,
        peaks,
        potential_col="potential_v",
        current_col="current_corrected_a",
        title="Simulated CV After Smoothing and Baseline Correction",
        current_unit="uA",
    )
    save_plot(PROCESSED_PLOT_PATH)

    print("Generating Markdown report...")
    generate_markdown_report(
        output_path=REPORT_PATH,
        title="Simulated CV Analysis Report",
        features=features,
        peaks=peaks,
        plot_path=PROCESSED_PLOT_PATH,
        notes=(
            "This report was generated from simulated cyclic voltammetry data. "
            "The integrated absolute current is used as a signal-shape descriptor, "
            "not as a calibrated electrochemical charge."
        ),
    )    

    print("\nAnalysis complete.")
    print(f"Raw data: {RAW_DATA_PATH}")
    print(f"Processed data: {PROCESSED_DATA_PATH}")
    print(f"Peak table: {PEAK_TABLE_PATH}")
    print(f"Raw plot: {RAW_PLOT_PATH}")
    print(f"Processed plot: {PROCESSED_PLOT_PATH}")
    print(f"Feature table: {FEATURE_TABLE_PATH}")
    print(f"Report: {REPORT_PATH}")


def _format_peak(peak: pd.Series) -> str:
    potential_v = peak["potential_v"]
    current_ua = peak["current_a"] * 1e6
    peak_type = peak["peak_type"]

    return (
        f"type={peak_type}, "
        f"potential={potential_v:.3f} V, "
        f"current={current_ua:.3f} uA"
    )


if __name__ == "__main__":
    main()