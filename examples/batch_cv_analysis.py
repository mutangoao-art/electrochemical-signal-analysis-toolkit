from __future__ import annotations

from pathlib import Path

from echem_signal_toolkit.batch import analyze_cv_directory, save_batch_summary
from echem_signal_toolkit.simulation import save_simulated_cv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BATCH_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "batch_cv"
BATCH_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "batch_cv_summary.csv"


def main() -> None:
    print("Generating simulated batch CV data...")

    sample_settings = [
        ("blank", 0.1, 1),
        ("sample_1uM", 1.0, 2),
        ("sample_5uM", 1.8, 3),
        ("sample_10uM", 2.6, 4),
    ]

    for sample_id, peak_scale, seed in sample_settings:
        save_simulated_cv(
            BATCH_RAW_DIR / f"{sample_id}.csv",
            peak_scale=peak_scale,
            random_seed=seed,
        )

    print("Running batch CV analysis...")

    summary = analyze_cv_directory(
        BATCH_RAW_DIR,
        pattern="*.csv",
        current_unit="A",
        peak_prominence=0.5e-6,
        peak_distance=80,
    )

    save_batch_summary(summary, BATCH_SUMMARY_PATH)

    print("Batch analysis complete.")
    print(summary[["sample_id", "oxidation_peak_potential_v", "oxidation_peak_current_a"]])
    print(f"Batch summary: {BATCH_SUMMARY_PATH}")


if __name__ == "__main__":
    main()