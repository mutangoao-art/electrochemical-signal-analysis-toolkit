from __future__ import annotations

from pathlib import Path

from echem_signal_toolkit.batch import analyze_dpv_directory, save_batch_summary
from echem_signal_toolkit.simulation import save_simulated_dpv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BATCH_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "batch_dpv"
BATCH_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "batch_dpv_summary.csv"


def main() -> None:
    print("Generating simulated batch DPV data...")

    sample_settings = [
        ("blank", 0.4e-6, 1),
        ("sample_1uM", 1.5e-6, 2),
        ("sample_5uM", 3.0e-6, 3),
        ("sample_10uM", 5.0e-6, 4),
        ("sample_20uM", 8.5e-6, 5),
    ]

    for sample_id, peak_amplitude_a, seed in sample_settings:
        save_simulated_dpv(
            BATCH_RAW_DIR / f"{sample_id}.csv",
            peak_amplitude_a=peak_amplitude_a,
            random_seed=seed,
        )

    print("Running batch DPV analysis...")

    summary = analyze_dpv_directory(
        BATCH_RAW_DIR,
        pattern="*.csv",
        current_unit="A",
        peak_prominence=0.2e-6,
        peak_distance=60,
    )

    save_batch_summary(summary, BATCH_SUMMARY_PATH)

    print("Batch DPV analysis complete.")
    print(summary[["sample_id", "peak_potential_v", "peak_current_a"]])
    print(f"Batch summary: {BATCH_SUMMARY_PATH}")


if __name__ == "__main__":
    main()