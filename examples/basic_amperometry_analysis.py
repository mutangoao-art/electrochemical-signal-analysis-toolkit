from __future__ import annotations

from pathlib import Path

import pandas as pd

from echem_signal_toolkit.amperometry import analyze_amperometry_channel
from echem_signal_toolkit.plotting import plot_amperometry, save_plot
from echem_signal_toolkit.simulation import save_simulated_amperometry


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "simulated_amperometry.csv"
SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_amperometry_summary.csv"
PLOT_PATH = PROJECT_ROOT / "data" / "processed" / "simulated_amperometry_it_curve.png"


def main() -> None:
    print("Generating simulated amperometry data...")
    data = save_simulated_amperometry(RAW_DATA_PATH)

    print("Analyzing amperometry channels...")

    current_cols = [
        column for column in data.columns
        if column.startswith("i") and column.endswith("_a")
    ]

    rows = []

    for current_col in current_cols:
        result = analyze_amperometry_channel(
            data,
            current_col=current_col,
            baseline_window_s=(0, 15),
            response_window_s=(80, 100),
        )

        rows.append(
            {
                "sample_id": "simulated_amperometry",
                "file_name": RAW_DATA_PATH.name,
                **result,
            }
        )

    summary = pd.DataFrame(rows)

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_PATH, index=False)

    plot_amperometry(
        data,
        title="Simulated Amperometric i-t Curve",
        current_unit="nA",
    )
    save_plot(PLOT_PATH)

    print("Amperometry analysis complete.")
    print(summary)
    print(f"Raw data: {RAW_DATA_PATH}")
    print(f"Summary: {SUMMARY_PATH}")
    print(f"Plot: {PLOT_PATH}")


if __name__ == "__main__":
    main()