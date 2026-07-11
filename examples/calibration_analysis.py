from __future__ import annotations

from pathlib import Path

import numpy as np

from echem_signal_toolkit.calibration import (
    build_calibration_table,
    estimate_lod,
    fit_calibration_curve,
)
from echem_signal_toolkit.plotting import plot_calibration_curve, save_plot


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CALIBRATION_TABLE_PATH = PROJECT_ROOT / "data" / "processed" / "calibration_table.csv"
CALIBRATION_PLOT_PATH = PROJECT_ROOT / "data" / "processed" / "calibration_curve.png"


def main() -> None:
    concentrations = np.array([0, 1, 2, 5, 10, 20, 50], dtype=float)

    rng = np.random.default_rng(42)
    true_slope = 0.18e-6
    true_intercept = 0.08e-6
    noise = rng.normal(0, 0.04e-6, size=concentrations.size)

    signals = true_slope * concentrations + true_intercept + noise

    calibration = build_calibration_table(concentrations, signals)
    fit_result = fit_calibration_curve(calibration)

    blank_signals = np.array([0.07e-6, 0.08e-6, 0.10e-6, 0.09e-6, 0.08e-6])
    lod = estimate_lod(blank_signals, slope=fit_result["slope"])

    CALIBRATION_TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    calibration.to_csv(CALIBRATION_TABLE_PATH, index=False)

    plot_calibration_curve(
        calibration,
        fit_result,
        concentration_unit="uM",
        signal_unit="A",
    )
    save_plot(CALIBRATION_PLOT_PATH)

    print("Calibration analysis complete.")
    print(f"Slope: {fit_result['slope']:.6g} A/uM")
    print(f"Intercept: {fit_result['intercept']:.6g} A")
    print(f"R-squared: {fit_result['r_squared']:.4f}")
    print(f"Estimated LOD: {lod:.6g} uM")
    print(f"Calibration table: {CALIBRATION_TABLE_PATH}")
    print(f"Calibration plot: {CALIBRATION_PLOT_PATH}")


if __name__ == "__main__":
    main()