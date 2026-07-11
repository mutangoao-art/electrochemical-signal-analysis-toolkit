from __future__ import annotations

from pathlib import Path

import pandas as pd
import numpy as np

from echem_signal_toolkit.calibration import (
    calibration_performance_summary,
    estimate_lod,
    estimate_loq,
    fit_replicate_calibration_curve,
    summarize_replicates,
)
from echem_signal_toolkit.plotting import plot_replicate_calibration_curve, save_plot
from echem_signal_toolkit.report import generate_calibration_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_TABLE_PATH = PROJECT_ROOT / "data" / "processed" / "replicate_calibration_raw.csv"
SUMMARY_TABLE_PATH = PROJECT_ROOT / "data" / "processed" / "replicate_calibration_summary.csv"
PERFORMANCE_TABLE_PATH = PROJECT_ROOT / "data" / "processed" / "replicate_calibration_performance.csv"
PLOT_PATH = PROJECT_ROOT / "data" / "processed" / "replicate_calibration_curve.png"
REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "replicate_calibration_report.md"


def main() -> None:
    print("Generating replicate calibration data...")

    calibration = _generate_replicate_calibration_data()

    print("Summarizing replicates...")
    replicate_summary = summarize_replicates(calibration)

    print("Fitting calibration curve using replicate means...")
    fit_result = fit_replicate_calibration_curve(replicate_summary)

    blank_signals = calibration.loc[
        calibration["concentration"] == 0.0,
        "signal",
    ]

    lod = estimate_lod(blank_signals, slope=fit_result["slope"])
    loq = estimate_loq(blank_signals, slope=fit_result["slope"])

    performance = calibration_performance_summary(
        fit_result=fit_result,
        lod=lod,
        loq=loq,
        concentration_unit="uM",
        signal_unit="A",
    )

    print("Saving outputs...")
    RAW_TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    calibration.to_csv(RAW_TABLE_PATH, index=False)
    replicate_summary.to_csv(SUMMARY_TABLE_PATH, index=False)
    pd.DataFrame([performance]).to_csv(PERFORMANCE_TABLE_PATH, index=False)

    plot_replicate_calibration_curve(
        replicate_summary,
        fit_result,
        concentration_unit="uM",
        signal_unit="A",
    )
    save_plot(PLOT_PATH)

    generate_calibration_report(
        output_path=REPORT_PATH,
        title="Replicate Calibration Analysis Report",
        performance=performance,
        replicate_summary=replicate_summary,
        plot_path=PLOT_PATH,
        notes=(
            "This report summarizes a simulated replicate calibration workflow. "
            "LOD and LOQ are estimated from blank replicate variability and "
            "the fitted calibration slope."
        ),
    )

    print("Replicate calibration analysis complete.")
    print(f"Sensitivity: {performance['sensitivity']:.6g} {performance['sensitivity_unit']}")
    print(f"R-squared: {performance['r_squared']:.4f}")
    print(f"LOD: {performance['lod']:.6g} {performance['lod_unit']}")
    print(f"LOQ: {performance['loq']:.6g} {performance['loq_unit']}")
    print(f"Raw table: {RAW_TABLE_PATH}")
    print(f"Summary table: {SUMMARY_TABLE_PATH}")
    print(f"Performance table: {PERFORMANCE_TABLE_PATH}")
    print(f"Plot: {PLOT_PATH}")
    print(f"Report: {REPORT_PATH}")


def _generate_replicate_calibration_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)

    concentrations = [0, 1, 5, 10, 20, 50]
    n_replicates = 3

    true_slope = 0.22e-6
    true_intercept = 0.15e-6
    base_noise_std = 0.12e-6
    relative_noise = 0.04

    rows = []

    for concentration in concentrations:
        expected_signal = true_slope * concentration + true_intercept
        noise_std = base_noise_std + relative_noise * expected_signal

        for replicate in range(1, n_replicates + 1):
            signal = expected_signal + rng.normal(0.0, noise_std)

            rows.append(
                {
                    "sample_id": f"{concentration}uM_rep{replicate}",
                    "concentration": float(concentration),
                    "replicate": replicate,
                    "signal": signal,
                }
            )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    main()