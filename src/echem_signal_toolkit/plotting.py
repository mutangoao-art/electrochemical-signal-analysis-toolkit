from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_cv(
    df: pd.DataFrame,
    *,
    potential_col: str = "potential_v",
    current_col: str = "current_a",
    title: str = "Cyclic Voltammetry",
    current_unit: str = "uA",
    ax=None,
):
    """
    Plot a cyclic voltammogram.

    Parameters
    ----------
    df:
        CV dataframe.
    potential_col:
        Name of potential column.
    current_col:
        Name of current column.
    title:
        Plot title.
    current_unit:
        Display unit for current: A, mA, uA, or nA.
    ax:
        Optional matplotlib axis.

    Returns
    -------
    matplotlib.axes.Axes
        Plot axis.
    """
    _require_columns(df, [potential_col, current_col])

    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5))

    current_scale, current_label = _current_display_scale(current_unit)

    ax.plot(
        df[potential_col],
        df[current_col] * current_scale,
        linewidth=1.8,
    )

    ax.set_title(title)
    ax.set_xlabel("Potential (V)")
    ax.set_ylabel(f"Current ({current_label})")
    ax.grid(True, alpha=0.3)

    return ax


def plot_cv_with_peaks(
    df: pd.DataFrame,
    peaks: pd.DataFrame,
    *,
    potential_col: str = "potential_v",
    current_col: str = "current_a",
    title: str = "CV Peak Detection",
    current_unit: str = "uA",
    ax=None,
):
    """
    Plot CV data and annotate detected peaks.
    """
    ax = plot_cv(
        df,
        potential_col=potential_col,
        current_col=current_col,
        title=title,
        current_unit=current_unit,
        ax=ax,
    )

    current_scale, _ = _current_display_scale(current_unit)

    if not peaks.empty:
        oxidation_peaks = peaks[peaks["peak_type"] == "oxidation"]
        reduction_peaks = peaks[peaks["peak_type"] == "reduction"]

        ax.scatter(
            oxidation_peaks["potential_v"],
            oxidation_peaks["current_a"] * current_scale,
            marker="o",
            color="tab:red",
            label="Oxidation peak",
            zorder=3,
        )

        ax.scatter(
            reduction_peaks["potential_v"],
            reduction_peaks["current_a"] * current_scale,
            marker="s",
            color="tab:blue",
            label="Reduction peak",
            zorder=3,
        )

        ax.legend()

    return ax


def save_plot(
    file_path: str | Path,
    *,
    dpi: int = 300,
    close: bool = True,
) -> None:
    """
    Save the current matplotlib figure.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(file_path, dpi=dpi, bbox_inches="tight")

    if close:
        plt.close()

def plot_calibration_curve(
    df: pd.DataFrame,
    fit_result: dict[str, float | int],
    *,
    concentration_col: str = "concentration",
    signal_col: str = "signal",
    title: str = "Calibration Curve",
    concentration_unit: str = "uM",
    signal_unit: str = "A",
    ax=None,
):
    """
    Plot calibration data and fitted linear regression line.
    """
    _require_columns(df, [concentration_col, signal_col])

    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5))

    x = df[concentration_col].to_numpy(dtype=float)
    y = df[signal_col].to_numpy(dtype=float)

    x_fit = pd.Series([x.min(), x.max()])
    y_fit = fit_result["slope"] * x_fit + fit_result["intercept"]

    ax.scatter(x, y, color="tab:blue", label="Data", zorder=3)
    ax.plot(x_fit, y_fit, color="tab:red", label="Linear fit")

    ax.set_title(title)
    ax.set_xlabel(f"Concentration ({concentration_unit})")
    ax.set_ylabel(f"Signal ({signal_unit})")
    ax.grid(True, alpha=0.3)

    r_squared = fit_result["r_squared"]
    slope = fit_result["slope"]
    intercept = fit_result["intercept"]

    ax.text(
        0.05,
        0.95,
        f"y = {slope:.3g}x + {intercept:.3g}\nR² = {r_squared:.4f}",
        transform=ax.transAxes,
        va="top",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
    )

    ax.legend()

    return ax

def plot_replicate_calibration_curve(
    replicate_summary: pd.DataFrame,
    fit_result: dict[str, float | int],
    *,
    concentration_col: str = "concentration",
    signal_mean_col: str = "signal_mean",
    signal_std_col: str = "signal_std",
    title: str = "Replicate Calibration Curve",
    concentration_unit: str = "uM",
    signal_unit: str = "A",
    ax=None,
):
    """
    Plot replicate calibration data with error bars and fitted line.
    """
    _require_columns(
        replicate_summary,
        [concentration_col, signal_mean_col, signal_std_col],
    )

    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5))

    x = replicate_summary[concentration_col].to_numpy(dtype=float)
    y = replicate_summary[signal_mean_col].to_numpy(dtype=float)
    yerr = replicate_summary[signal_std_col].to_numpy(dtype=float)

    x_fit = pd.Series([x.min(), x.max()])
    y_fit = fit_result["slope"] * x_fit + fit_result["intercept"]

    ax.errorbar(
        x,
        y,
        yerr=yerr,
        fmt="o",
        color="tab:blue",
        ecolor="tab:gray",
        capsize=4,
        label="Mean ± SD",
        zorder=3,
    )

    ax.plot(x_fit, y_fit, color="tab:red", label="Linear fit")

    ax.set_title(title)
    ax.set_xlabel(f"Concentration ({concentration_unit})")
    ax.set_ylabel(f"Signal ({signal_unit})")
    ax.grid(True, alpha=0.3)

    ax.text(
        0.05,
        0.95,
        f"y = {fit_result['slope']:.3g}x + {fit_result['intercept']:.3g}\n"
        f"R² = {fit_result['r_squared']:.4f}",
        transform=ax.transAxes,
        va="top",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
    )

    ax.legend()

    return ax

def _current_display_scale(current_unit: str) -> tuple[float, str]:
    normalized_unit = current_unit.strip().lower()

    scales = {
        "a": (1.0, "A"),
        "ma": (1e3, "mA"),
        "ua": (1e6, "uA"),
        "µa": (1e6, "uA"),
        "na": (1e9, "nA"),
    }

    if normalized_unit not in scales:
        allowed = ", ".join(scales)
        raise ValueError(f"Unsupported current display unit: {current_unit}. Allowed: {allowed}")

    return scales[normalized_unit]


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]

    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required column(s): {missing_text}")