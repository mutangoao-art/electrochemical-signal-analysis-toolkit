from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

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

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "full_biosensor_workflow"

RAW_TABLE_PATH = OUTPUT_DIR / "replicate_measurements.csv"
SUMMARY_TABLE_PATH = OUTPUT_DIR / "replicate_summary.csv"
PERFORMANCE_TABLE_PATH = OUTPUT_DIR / "calibration_performance.csv"
PLOT_PATH = OUTPUT_DIR / "calibration_curve.png"
REPORT_PATH = OUTPUT_DIR / "calibration_report.md"


def main() -> None:
    print("Generating simulated biosensor replicate measurements...")
    measurements = generate_biosensor_replicates()

    print("Summarizing replicate measurements...")
    replicate_summary = summarize_replicates(measurements)

    print("Fitting calibration curve...")
    fit_result = fit_replicate_calibration_curve(replicate_summary)

    blank_signals = measurements.loc[
        measurements["concentration"] == 0.0,
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
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    measurements.to_csv(RAW_TABLE_PATH, index=False)
    replicate_summary.to_csv(SUMMARY_TABLE_PATH, index=False)
    pd.DataFrame([performance]).to_csv(PERFORMANCE_TABLE_PATH, index=False)

    plot_replicate_calibration_curve(
        replicate_summary,
        fit_result,
        title="Simulated Biosensor Calibration",
        concentration_unit="uM",
        signal_unit="A",
    )
    save_plot(PLOT_PATH)

    generate_calibration_report(
        output_path=REPORT_PATH,
        title="Simulated Biosensor Calibration Report",
        performance=performance,
        replicate_summary=replicate_summary,
        plot_path=PLOT_PATH,
        notes=(
            "This workflow demonstrates replicate-aware calibration analysis "
            "for simulated electrochemical biosensor data. The analytical "
            "signal is modeled as a concentration-dependent current response."
        ),
    )

    print("Workflow complete.")
    print(f"Sensitivity: {performance['sensitivity']:.6g} {performance['sensitivity_unit']}")
    print(f"R-squared: {performance['r_squared']:.4f}")
    print(f"LOD: {performance['lod']:.6g} {performance['lod_unit']}")
    print(f"LOQ: {performance['loq']:.6g} {performance['loq_unit']}")
    print(f"Measurements: {RAW_TABLE_PATH}")
    print(f"Summary: {SUMMARY_TABLE_PATH}")
    print(f"Performance: {PERFORMANCE_TABLE_PATH}")
    print(f"Plot: {PLOT_PATH}")
    print(f"Report: {REPORT_PATH}")


def generate_biosensor_replicates() -> pd.DataFrame:
    """
    Generate simulated replicate measurements for a biosensor calibration curve.
    """
    rng = np.random.default_rng(7)

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