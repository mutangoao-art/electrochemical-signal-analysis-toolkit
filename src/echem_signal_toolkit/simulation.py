from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_simulated_cv(
    *,
    start_v: float = -0.2,
    vertex_v: float = 0.8,
    end_v: float = -0.2,
    points_per_segment: int = 500,
    scan_rate_v_s: float = 0.1,
    cycle: int = 1,
    noise_std_a: float = 0.15e-6,
    random_seed: int | None = 42,
    peak_scale: float = 1.0
) -> pd.DataFrame:
    """
    Generate a simplified simulated cyclic voltammetry curve.

    The simulated signal contains:
    - a triangular potential sweep
    - capacitive/background current
    - one oxidation peak
    - one reduction peak
    - random Gaussian noise

    Returns
    -------
    pandas.DataFrame
        Simulated CV data with columns:
        time_s, potential_v, current_a, cycle
    """
    rng = np.random.default_rng(random_seed)

    forward = np.linspace(start_v, vertex_v, points_per_segment)
    reverse = np.linspace(vertex_v, end_v, points_per_segment)
    potential_v = np.concatenate([forward, reverse])

    potential_step = abs(vertex_v - start_v) / max(points_per_segment - 1, 1)
    time_step = potential_step / scan_rate_v_s
    time_s = np.arange(potential_v.size) * time_step

    background_current = 0.8e-6 * potential_v + 0.2e-6
    oxidation_peak = peak_scale * _gaussian(
        potential_v,
        center=0.45,
        amplitude=5.0e-6,
        width=0.055,
    )

    reduction_peak = -peak_scale * _gaussian(
        potential_v,
        center=0.25,
        amplitude=3.2e-6,
        width=0.065,
    )

    # Make the forward scan mostly oxidation-like and reverse scan mostly reduction-like.
    direction = np.concatenate(
        [
            np.ones(points_per_segment),
            -np.ones(points_per_segment),
        ]
    )

    faradaic_current = np.where(
        direction > 0,
        oxidation_peak,
        reduction_peak,
    )

    noise = rng.normal(loc=0.0, scale=noise_std_a, size=potential_v.size)

    current_a = background_current + faradaic_current + noise

    return pd.DataFrame(
        {
            "time_s": time_s,
            "potential_v": potential_v,
            "current_a": current_a,
            "cycle": cycle,
        }
    )


def save_simulated_cv(
    file_path: str | Path,
    **kwargs,
) -> pd.DataFrame:
    """
    Generate simulated CV data and save it as a CSV file.

    Returns the generated dataframe.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate_simulated_cv(**kwargs)
    df.to_csv(file_path, index=False)

    return df

def generate_simulated_dpv(
    *,
    start_v: float = -0.2,
    end_v: float = 0.8,
    n_points: int = 500,
    peak_center_v: float = 0.42,
    peak_amplitude_a: float = 4.0e-6,
    peak_width_v: float = 0.055,
    background_slope_a_v: float = 0.25e-6,
    background_intercept_a: float = 0.15e-6,
    noise_std_a: float = 0.08e-6,
    random_seed: int | None = 42,
) -> pd.DataFrame:
    """
    Generate simplified simulated differential pulse voltammetry data.

    Returns columns:
    - potential_v
    - current_a
    """
    rng = np.random.default_rng(random_seed)

    potential_v = np.linspace(start_v, end_v, n_points)

    background = background_slope_a_v * potential_v + background_intercept_a

    peak = _gaussian(
        potential_v,
        center=peak_center_v,
        amplitude=peak_amplitude_a,
        width=peak_width_v,
    )

    noise = rng.normal(0.0, noise_std_a, size=n_points)

    current_a = background + peak + noise

    return pd.DataFrame(
        {
            "potential_v": potential_v,
            "current_a": current_a,
        }
    )


def save_simulated_dpv(
    file_path: str | Path,
    **kwargs,
) -> pd.DataFrame:
    """
    Generate simulated DPV data and save it as CSV.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate_simulated_dpv(**kwargs)
    df.to_csv(file_path, index=False)

    return df

def generate_simulated_amperometry(
    *,
    run_time_s: float = 100.0,
    sample_interval_s: float = 0.5,
    channels: list[str] | None = None,
    baseline_current_a: float = -8.0e-9,
    response_current_a: float = -25.0e-9,
    response_start_s: float = 20.0,
    tau_s: float = 12.0,
    noise_std_a: float = 0.8e-9,
    drift_a_per_s: float = 0.02e-9,
    random_seed: int | None = 42,
) -> pd.DataFrame:
    """
    Generate simulated amperometric current-time data.

    The simulated signal contains:
    - a baseline current
    - a concentration-like response after response_start_s
    - exponential approach to steady state
    - small linear drift
    - Gaussian noise
    - multiple channels with slightly different response scales
    """
    if channels is None:
        channels = ["i4", "i6", "i8"]

    rng = np.random.default_rng(random_seed)

    time_s = np.arange(
        sample_interval_s,
        run_time_s + sample_interval_s,
        sample_interval_s,
    )

    data: dict[str, np.ndarray] = {"time_s": time_s}

    channel_scales = np.linspace(0.8, 1.2, len(channels))

    for channel, scale in zip(channels, channel_scales):
        response = np.zeros_like(time_s)

        response_region = time_s >= response_start_s
        response[response_region] = (
            response_current_a
            * scale
            * (1.0 - np.exp(-(time_s[response_region] - response_start_s) / tau_s))
        )

        drift = drift_a_per_s * time_s
        noise = rng.normal(0.0, noise_std_a, size=time_s.size)

        current = baseline_current_a + response + drift + noise

        data[f"{channel}_a"] = current

    return pd.DataFrame(data)


def save_simulated_amperometry(
    file_path: str | Path,
    **kwargs,
) -> pd.DataFrame:
    """
    Generate simulated amperometry data and save it as CSV.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate_simulated_amperometry(**kwargs)
    df.to_csv(file_path, index=False)

    return df

def _gaussian(
    x: np.ndarray,
    *,
    center: float,
    amplitude: float,
    width: float,
) -> np.ndarray:
    return amplitude * np.exp(-0.5 * ((x - center) / width) ** 2)