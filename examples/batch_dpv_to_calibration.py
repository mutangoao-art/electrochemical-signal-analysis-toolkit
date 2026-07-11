from __future__ import annotations

from pathlib import Path

from echem_signal_toolkit.batch import analyze_dpv_directory, save_batch_summary
from echem_signal_toolkit.calibration import (
    calibration_from_batch_summary,
    estimate_lod_from_batch_summary,
    fit_calibration_curve,
)
from echem_signal_toolkit.plotting import plot_calibration_curve, save_plot
from echem_signal_toolkit.simulation import save_simulated_dpv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "batch_dpv_calibration"
SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "batch_dpv_calibration_summary.csv"
CALIBRATION_TABLE_PATH = PROJECT_ROOT / "data" / "processed" / "batch_dpv_calibration_table.csv"
CALIBRATION_PLOT_PATH = PROJECT_ROOT / "data" / "processed" / "batch_dpv_calibration_curve.png"


def main() -> None:
    print("Generating simulated DPV files for calibration workflow...")

    sample_settings = [
        ("blank_1", 0.35e-6, 1),
        ("blank_2", 0.40e-6, 2),
        ("blank_3", 0.45e-6, 3),
        ("sample_1uM", 1.5e-6, 4),
        ("sample_5uM", 3.0e-6, 5),
        ("sample_10uM", 5.0e-6, 6),
        ("sample_20uM", 8.5e-6, 7),
    ]

    for sample_id, peak_amplitude_a, seed in sample_settings:
        save_simulated_dpv(
            RAW_DIR / f"{sample_id}.csv",
            peak_amplitude_a=peak_amplitude_a,
            random_seed=seed,
        )

    print("Running batch DPV analysis...")
    summary = analyze_dpv_directory(
        RAW_DIR,
        pattern="*.csv",
        peak_prominence=0.2e-6,
        peak_distance=60,
    )

    save_batch_summary(summary, SUMMARY_PATH)

    concentration_map = {
        "blank_1": 0.0,
        "blank_2": 0.0,
        "blank_3": 0.0,
        "sample_1uM": 1.0,
        "sample_5uM": 5.0,
        "sample_10uM": 10.0,
        "sample_20uM": 20.0,
    }

    print("Building DPV calibration table from batch summary...")
    calibration = calibration_from_batch_summary(
        summary,
        concentration_map=concentration_map,
        signal_col="peak_current_a",
    )

    fit_result = fit_calibration_curve(calibration)

    lod = estimate_lod_from_batch_summary(
        summary,
        concentration_map=concentration_map,
        blank_sample_ids=["blank_1", "blank_2", "blank_3"],
        signal_col="peak_current_a",
    )

    CALIBRATION_TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    calibration.to_csv(CALIBRATION_TABLE_PATH, index=False)

    plot_calibration_curve(
        calibration,
        fit_result,
        concentration_unit="uM",
        signal_unit="A",
    )
    save_plot(CALIBRATION_PLOT_PATH)

    print("Batch DPV-to-calibration workflow complete.")
    print(f"Slope: {fit_result['slope']:.6g} A/uM")
    print(f"Intercept: {fit_result['intercept']:.6g} A")
    print(f"R-squared: {fit_result['r_squared']:.4f}")
    print(f"Estimated LOD: {lod:.6g} uM")
    print(f"Summary: {SUMMARY_PATH}")
    print(f"Calibration table: {CALIBRATION_TABLE_PATH}")
    print(f"Calibration plot: {CALIBRATION_PLOT_PATH}")


if __name__ == "__main__":
    main()