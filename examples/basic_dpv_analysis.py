from __future__ import annotations

from pathlib import Path

from echem_signal_toolkit.dpv import analyze_dpv, dpv_features_to_dataframe
from echem_signal_toolkit.io import load_cv_data
from echem_signal_toolkit.plotting import plot_cv_with_peaks, save_plot
from echem_signal_toolkit.report import generate_markdown_report
from echem_signal_toolkit.simulation import save_simulated_dpv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "simulated_dpv.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_dpv_processed.csv"
PEAK_TABLE_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_dpv_peaks.csv"
FEATURE_TABLE_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_dpv_features.csv"
PLOT_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_dpv_peaks.png"
REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_dpv_report.md"


def main() -> None:
    print("Generating simulated DPV data...")
    save_simulated_dpv(RAW_DATA_PATH)

    print("Loading DPV data...")
    dpv_data = load_cv_data(RAW_DATA_PATH)

    print("Analyzing DPV signal...")
    processed, peaks, features = analyze_dpv(
        dpv_data,
        peak_prominence=0.5e-6,
        peak_distance=80,
    )

    feature_table = dpv_features_to_dataframe(features)

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    processed.to_csv(PROCESSED_DATA_PATH, index=False)
    peaks.to_csv(PEAK_TABLE_PATH, index=False)
    feature_table.to_csv(FEATURE_TABLE_PATH, index=False)

    plot_cv_with_peaks(
        processed,
        peaks,
        potential_col="potential_v",
        current_col="current_corrected_a",
        title="Simulated DPV Peak Detection",
        current_unit="uA",
    )
    save_plot(PLOT_PATH)

    generate_markdown_report(
        output_path=REPORT_PATH,
        title="Simulated DPV Analysis Report",
        features=features,
        peaks=peaks,
        plot_path=PLOT_PATH,
        notes=(
            "This report was generated from simulated differential pulse "
            "voltammetry data. The main analytical signal is the oxidation "
            "peak current after smoothing and baseline correction."
        ),
    )

    print("DPV analysis complete.")
    print(f"Peak potential: {features['peak_potential_v']:.3f} V")
    print(f"Peak current: {features['peak_current_a'] * 1e6:.3f} uA")
    print(f"Processed data: {PROCESSED_DATA_PATH}")
    print(f"Peak table: {PEAK_TABLE_PATH}")
    print(f"Feature table: {FEATURE_TABLE_PATH}")
    print(f"Plot: {PLOT_PATH}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()