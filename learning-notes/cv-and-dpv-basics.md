
# CV and DPV Basics for Electrochemical Biosensor Signal Analysis

## Purpose

This note summarizes the electrochemical signal concepts used in this project. The goal is to connect the code workflow with common biosensor data analysis tasks, including preprocessing, peak detection, feature extraction, calibration, and limit of detection estimation.

## Cyclic Voltammetry

Cyclic voltammetry (CV) measures current while the electrode potential is swept forward and then reversed. The resulting current-potential curve can provide information about redox behavior, electrode surface processes, and sensor response.

In a simplified CV workflow, the key data columns are:

| Column | Meaning |
|---|---|
| `potential_v` | Applied electrode potential in volts |
| `current_a` | Measured current in amperes |
| `time_s` | Time in seconds, if available |
| `cycle` | Cycle or segment number, if available |

## CV Features

Common CV features include:

| Feature | Meaning |
|---|---|
| Oxidation peak potential | Potential where the oxidation current reaches a local maximum |
| Oxidation peak current | Current at the oxidation peak |
| Reduction peak potential | Potential where the reduction current reaches a local minimum |
| Reduction peak current | Current at the reduction peak |
| Peak separation | Difference between oxidation and reduction peak potentials |
| Current ratio | Ratio between oxidation and reduction peak currents |

These features can help compare electrochemical behavior across samples, electrode modifications, or analyte concentrations.

## Differential Pulse Voltammetry

Differential pulse voltammetry (DPV) is often used for quantitative electrochemical sensing. Compared with CV, DPV can provide sharper peaks and improved sensitivity by reducing background current effects.

In many biosensor workflows, the DPV peak current is used as the analytical signal for calibration.

Typical DPV features include:

| Feature | Meaning |
|---|---|
| Peak potential | Potential at the main oxidation peak |
| Peak current | Current at the main oxidation peak |
| Peak prominence | How strongly the peak stands out from the surrounding signal |
| Current range | Difference between maximum and minimum current |

## Why Preprocessing Is Needed

Raw electrochemical signals often contain noise, baseline drift, and background current. Preprocessing helps make feature extraction more reproducible.

This project currently includes:

- Savitzky-Golay smoothing
- Polynomial baseline correction
- Current normalization
- Standardized column naming and current unit conversion

These methods are intentionally simple in the first version, so the analysis flow remains transparent and easy to inspect.

## Peak Detection

Peak detection is used to locate local maxima or minima in electrochemical signals.

For CV:

- Oxidation peaks are detected as positive current peaks
- Reduction peaks are detected as negative current peaks

For DPV:

- The main oxidation peak is typically used as the analytical response

Peak detection parameters such as prominence and distance need to be adjusted depending on signal quality, sampling density, and expected peak shape.

## Calibration Curve

In biosensor analysis, calibration connects signal intensity to analyte concentration.

A common linear calibration model is:

```text
signal = slope * concentration + intercept
```

The slope indicates sensitivity. The coefficient of determination, R-squared, describes how well the linear model explains the observed response.

## Limit of Detection

The limit of detection (LOD) is commonly estimated using blank signal variability and calibration sensitivity:

```text
LOD = 3 * standard deviation of blank signal / slope
```

This project uses this formula as a first-pass LOD estimate. In real experimental reporting, the choice of blank measurements, number of replicates, calibration range, and statistical assumptions should be clearly documented.

## Current Project Workflow

The current toolkit supports the following workflows:

```text
CV data -> preprocessing -> peak detection -> feature extraction -> report
```

```text
DPV data -> preprocessing -> peak detection -> feature extraction -> report
```

```text
multiple CV files -> batch summary -> calibration curve -> LOD estimate
```

## Notes for Future Development

Planned improvements include:

- Better baseline correction methods
- Batch DPV analysis
- Replicate-aware calibration statistics
- More detailed report generation
- Support for additional electrochemical methods such as amperometry and EIS
- Compatibility presets for common instrument export formats
```