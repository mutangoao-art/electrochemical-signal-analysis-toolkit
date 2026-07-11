from __future__ import annotations

from pathlib import Path

from echem_signal_toolkit.amperometry import analyze_amperometry_directory
from echem_signal_toolkit.batch import save_batch_summary
from echem_signal_toolkit.simulation import save_simulated_amperometry


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BATCH_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "batch_amperometry"
BATCH_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "batch_amperometry_summary.csv"


def main() -> None:
    print("Generating simulated batch amperometry data...")

    sample_settings = [
        ("blank", -5.0e-9, 1),
        ("sample_low", -15.0e-9, 2),
        ("sample_mid", -30.0e-9, 3),
        ("sample_high", -55.0e-9, 4),
    ]

    for sample_id, response_current_a, seed in sample_settings:
        save_simulated_amperometry(
            BATCH_RAW_DIR / f"{sample_id}.csv",
            response_current_a=response_current_a,
            random_seed=seed,
        )

    print("Running batch amperometry analysis...")

    summary = analyze_amperometry_directory(
        BATCH_RAW_DIR,
        pattern="*.csv",
        channels=["i4", "i6", "i8"],
        baseline_window_s=(0, 15),
        response_window_s=(80, 100),
    )

    save_batch_summary(summary, BATCH_SUMMARY_PATH)

    print("Batch amperometry analysis complete.")
    print(summary[["sample_id", "channel", "response_current_a", "snr"]])
    print(f"Batch summary: {BATCH_SUMMARY_PATH}")


if __name__ == "__main__":
    main()