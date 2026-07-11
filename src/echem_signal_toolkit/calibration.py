from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import linregress


def fit_calibration_curve(
    df: pd.DataFrame,
    *,
    concentration_col: str = "concentration",
    signal_col: str = "signal",
) -> dict[str, float | int]:
    """
    Fit a linear calibration curve for biosensor response.

    The model is:

        signal = slope * concentration + intercept

    Returns regression statistics including slope, intercept, r-squared,
    p-value, and standard error.
    """
def calibration_from_batch_summary(
    summary: pd.DataFrame,
    *,
    concentration_map: dict[str, float],
    sample_id_col: str = "sample_id",
    signal_col: str = "oxidation_peak_current_a",
    output_concentration_col: str = "concentration",
    output_signal_col: str = "signal",
) -> pd.DataFrame:
    """
    Build a calibration table from a batch CV feature summary.

    Parameters
    ----------
    summary:
        Batch analysis summary table.
    concentration_map:
        Mapping from sample_id to concentration.
    sample_id_col:
        Column containing sample identifiers.
    signal_col:
        Feature column used as analytical signal.
    output_concentration_col:
        Name of the output concentration column.
    output_signal_col:
        Name of the output signal column.
    """
    _require_columns(summary, [sample_id_col, signal_col])

    records: list[dict[str, float | str]] = []

    for _, row in summary.iterrows():
        sample_id = row[sample_id_col]

        if sample_id not in concentration_map:
            continue

        records.append(
            {
                sample_id_col: sample_id,
                output_concentration_col: concentration_map[sample_id],
                output_signal_col: row[signal_col],
            }
        )

    if not records:
        raise ValueError("No summary rows matched the provided concentration_map")

    calibration = pd.DataFrame(records)
    calibration = calibration.sort_values(output_concentration_col).reset_index(drop=True)

    return calibration

def estimate_lod_from_batch_summary(
    summary: pd.DataFrame,
    *,
    concentration_map: dict[str, float],
    blank_sample_ids: list[str],
    sample_id_col: str = "sample_id",
    signal_col: str = "oxidation_peak_current_a",
) -> float:
    """
    Estimate LOD using blank samples in a batch summary table.

    The slope is fitted from the concentration-response data, and blank
    variability is estimated from rows whose sample_id is listed in
    blank_sample_ids.
    """
    _require_columns(summary, [sample_id_col, signal_col])

    calibration = calibration_from_batch_summary(
        summary,
        concentration_map=concentration_map,
        sample_id_col=sample_id_col,
        signal_col=signal_col,
    )

    fit_result = fit_calibration_curve(calibration)

    blank_rows = summary[summary[sample_id_col].isin(blank_sample_ids)]

    if len(blank_rows) < 2:
        raise ValueError("At least two blank rows are required for LOD estimation")

    return estimate_lod(
        blank_rows[signal_col],
        slope=fit_result["slope"],
    )

def fit_calibration_curve(
    df: pd.DataFrame,
    *,
    concentration_col: str = "concentration",
    signal_col: str = "signal",
) -> dict[str, float | int]:
    """
    Fit a linear calibration curve for biosensor response.

    The model is:

        signal = slope * concentration + intercept
    """
    _require_columns(df, [concentration_col, signal_col])

    clean = df[[concentration_col, signal_col]].dropna()

    if len(clean) < 2:
        raise ValueError("At least two calibration points are required")

    concentration = clean[concentration_col].to_numpy(dtype=float)
    signal = clean[signal_col].to_numpy(dtype=float)

    result = linregress(concentration, signal)

    return {
        "n_points": int(len(clean)),
        "slope": float(result.slope),
        "intercept": float(result.intercept),
        "r_value": float(result.rvalue),
        "r_squared": float(result.rvalue**2),
        "p_value": float(result.pvalue),
        "std_err": float(result.stderr),
    }
    
    _require_columns(df, [concentration_col, signal_col])

    clean = df[[concentration_col, signal_col]].dropna()

    if len(clean) < 2:
        raise ValueError("At least two calibration points are required")

    concentration = clean[concentration_col].to_numpy(dtype=float)
    signal = clean[signal_col].to_numpy(dtype=float)

    result = linregress(concentration, signal)

    return {
        "n_points": int(len(clean)),
        "slope": float(result.slope),
        "intercept": float(result.intercept),
        "r_value": float(result.rvalue),
        "r_squared": float(result.rvalue**2),
        "p_value": float(result.pvalue),
        "std_err": float(result.stderr),
    }


def predict_signal(
    concentration: float | np.ndarray,
    *,
    slope: float,
    intercept: float,
) -> float | np.ndarray:
    """
    Predict analytical signal from concentration using a linear model.
    """
    return slope * concentration + intercept


def estimate_lod(
    blank_signals: list[float] | np.ndarray | pd.Series,
    *,
    slope: float,
    multiplier: float = 3.0,
) -> float:
    """
    Estimate limit of detection using:

        LOD = multiplier * standard deviation of blank / slope

    A common choice is multiplier=3.
    """
    blank = np.asarray(blank_signals, dtype=float)

    if blank.size < 2:
        raise ValueError("At least two blank measurements are required")

    if slope == 0:
        raise ValueError("Slope must be non-zero for LOD estimation")

    blank_std = np.std(blank, ddof=1)

    return float(multiplier * blank_std / abs(slope))


def build_calibration_table(
    concentrations: list[float] | np.ndarray,
    signals: list[float] | np.ndarray,
) -> pd.DataFrame:
    """
    Build a simple calibration dataframe from concentration and signal arrays.
    """
    if len(concentrations) != len(signals):
        raise ValueError("concentrations and signals must have the same length")

    return pd.DataFrame(
        {
            "concentration": concentrations,
            "signal": signals,
        }
    )

def summarize_replicates(
    df: pd.DataFrame,
    *,
    concentration_col: str = "concentration",
    signal_col: str = "signal",
) -> pd.DataFrame:
    """
    Summarize replicate measurements by concentration.

    Returns mean, standard deviation, replicate count, and RSD percentage.
    """
    _require_columns(df, [concentration_col, signal_col])

    summary = (
        df.groupby(concentration_col, as_index=False)
        .agg(
            signal_mean=(signal_col, "mean"),
            signal_std=(signal_col, "std"),
            signal_count=(signal_col, "count"),
        )
        .sort_values(concentration_col)
        .reset_index(drop=True)
    )

    summary["signal_std"] = summary["signal_std"].fillna(0.0)

    summary["signal_rsd_percent"] = summary.apply(
        lambda row: _rsd_percent(row["signal_mean"], row["signal_std"]),
        axis=1,
    )

    return summary


def fit_replicate_calibration_curve(
    replicate_summary: pd.DataFrame,
    *,
    concentration_col: str = "concentration",
    signal_mean_col: str = "signal_mean",
) -> dict[str, float | int]:
    """
    Fit a calibration curve using replicate mean signals.
    """
    _require_columns(replicate_summary, [concentration_col, signal_mean_col])

    calibration = replicate_summary.rename(
        columns={
            concentration_col: "concentration",
            signal_mean_col: "signal",
        }
    )

    return fit_calibration_curve(calibration)


def estimate_loq(
    blank_signals: list[float] | np.ndarray | pd.Series,
    *,
    slope: float,
    multiplier: float = 10.0,
) -> float:
    """
    Estimate limit of quantification using:

        LOQ = multiplier * standard deviation of blank / slope

    A common choice is multiplier=10.
    """
    return estimate_lod(
        blank_signals,
        slope=slope,
        multiplier=multiplier,
    )


def calibration_performance_summary(
    *,
    fit_result: dict[str, float | int],
    lod: float | None = None,
    loq: float | None = None,
    concentration_unit: str = "uM",
    signal_unit: str = "A",
) -> dict[str, float | str | None]:
    """
    Build a compact summary of calibration performance.
    """
    return {
        "sensitivity": fit_result["slope"],
        "sensitivity_unit": f"{signal_unit}/{concentration_unit}",
        "intercept": fit_result["intercept"],
        "r_squared": fit_result["r_squared"],
        "lod": lod,
        "lod_unit": concentration_unit,
        "loq": loq,
        "loq_unit": concentration_unit,
        "n_points": fit_result["n_points"],
    }


def _rsd_percent(mean: float, std: float) -> float | None:
    if mean == 0:
        return None

    return float(abs(std / mean) * 100)

def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]

    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required column(s): {missing_text}")