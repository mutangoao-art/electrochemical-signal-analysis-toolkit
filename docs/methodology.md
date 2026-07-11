
# Methodology

## Overview

This document describes the analysis methodology implemented in the Electrochemical Signal Analysis Toolkit.

The toolkit is designed to support reproducible analysis of electrochemical biosensor data, with the current version focused on cyclic voltammetry (CV), differential pulse voltammetry (DPV), batch feature extraction, calibration curve fitting, limit of detection estimation, limit of quantification estimation, and Markdown report generation.

The goal is not to replace expert electrochemical interpretation, but to provide a transparent and reusable computational workflow for common signal processing and quantitative analysis tasks.

## Data Standardization

Electrochemical instruments and analysis software often export data with different column names, units, delimiters, and optional metadata. To make downstream analysis consistent, the toolkit standardizes imported data into a small set of internal column names.

| Standard Column | Meaning |
|---|---|
| `potential_v` | Applied potential in volts |
| `current_a` | Measured current in amperes |
| `time_s` | Time in seconds, if available |
| `cycle` | Cycle or segment number, if available |

The import workflow supports explicit column mapping and current unit conversion. For example, current values exported in microamperes can be converted to amperes before analysis.

This standardization allows preprocessing, plotting, peak detection, feature extraction, and reporting functions to operate on a consistent data structure.

## Simulated Data

The toolkit includes simulated CV and DPV data generators. These simulated datasets are used for examples, tests, and demonstration workflows.

Simulated CV data include:

- A triangular potential sweep
- Background current
- Oxidation and reduction peaks
- Gaussian noise
- Optional scaling of peak amplitude

Simulated DPV data include:

- A linear potential sweep
- Background current
- A main oxidation peak
- Gaussian noise

The simulated signals are simplified and are not intended to reproduce every physical detail of real electrochemical experiments. They are used to make the analysis pipeline runnable without requiring proprietary or unpublished experimental data.

## Signal Preprocessing

Raw electrochemical signals may contain noise, background current, baseline drift, and instrument-dependent artifacts. The toolkit currently provides simple and transparent preprocessing methods.

### Smoothing

Current signals can be smoothed using a Savitzky-Golay filter. This method is useful for reducing high-frequency noise while preserving approximate peak shape.

Key parameters include:

| Parameter | Meaning |
|---|---|
| `window_length` | Number of points used in the smoothing window |
| `polyorder` | Polynomial order used within the smoothing window |

The smoothing window should be selected carefully. A window that is too small may leave noise, while a window that is too large may distort peak shape.

### Baseline Correction

The current implementation uses polynomial baseline correction based on edge regions of the signal. The baseline is estimated from the beginning and end portions of the voltammogram, then subtracted from the signal.

Key parameters include:

| Parameter | Meaning |
|---|---|
| `degree` | Polynomial degree used for baseline fitting |
| `edge_fraction` | Fraction of points from each edge used to estimate the baseline |

This method is intentionally simple and interpretable. It is suitable for demonstration and moderately clean simulated or experimental signals, but more advanced baseline correction may be needed for complex real datasets.

### Normalization

The toolkit supports current normalization methods such as maximum absolute normalization and min-max normalization. Normalization can help compare signal shapes, but quantitative calibration should generally use physically meaningful current values rather than normalized current.

## Peak Detection

Peak detection is performed using local extrema and prominence-based criteria.

### CV Peak Detection

For CV data, the toolkit can detect:

- Oxidation peaks as positive current peaks
- Reduction peaks as negative current peaks

The reduction peak detection is performed by applying peak detection to the negative current signal.

Important parameters include:

| Parameter | Meaning |
|---|---|
| `prominence` | Minimum required peak prominence |
| `distance` | Minimum distance between detected peaks, in data points |

Detected CV peaks are returned in a table containing peak index, peak potential, peak current, peak type, and optional prominence.

### DPV Peak Detection

For DPV data, the main oxidation peak is commonly used as the analytical signal for quantitative biosensing. The toolkit applies smoothing, baseline correction, and oxidation peak detection, then extracts the main peak current and peak potential.

## Feature Extraction

Feature extraction converts processed electrochemical signals into quantitative descriptors.

### CV Features

The CV feature extraction workflow includes:

| Feature | Meaning |
|---|---|
| `oxidation_peak_potential_v` | Potential of the main oxidation peak |
| `oxidation_peak_current_a` | Current of the main oxidation peak |
| `reduction_peak_potential_v` | Potential of the main reduction peak |
| `reduction_peak_current_a` | Current of the main reduction peak |
| `peak_separation_v` | Difference between oxidation and reduction peak potentials |
| `oxidation_reduction_current_ratio_abs` | Absolute oxidation/reduction current ratio |
| `current_range_a` | Difference between maximum and minimum current |
| `integrated_abs_current_av` | Absolute current integrated over potential |

The integrated absolute current is used as a signal-shape descriptor. It should not be interpreted as formal electrochemical charge unless scan rate, time-domain integration, and experimental context are handled carefully.

### DPV Features

The DPV feature extraction workflow includes:

| Feature | Meaning |
|---|---|
| `peak_potential_v` | Potential of the main DPV peak |
| `peak_current_a` | Current of the main DPV peak |
| `peak_prominence_a` | Prominence of the detected peak |
| `current_range_a` | Difference between maximum and minimum current |

For many biosensor workflows, `peak_current_a` is the primary analytical signal used for calibration.

## Batch Analysis

Batch analysis allows multiple CV or DPV files to be processed with the same analysis settings. Each file is analyzed independently, and the extracted features are combined into a summary table.

A typical batch workflow is:

```text
multiple input files -> preprocessing -> peak detection -> feature extraction -> summary table
```

The batch summary can then be used for concentration-response analysis or calibration.

## Calibration Analysis

Calibration analysis relates an analytical signal to analyte concentration.

The current implementation uses a linear calibration model:

```text
signal = slope * concentration + intercept
```

The fitted calibration result includes:

| Metric | Meaning |
|---|---|
| `slope` | Sensitivity of the sensor response |
| `intercept` | Estimated signal at zero concentration |
| `r_squared` | Coefficient of determination |
| `p_value` | p-value from linear regression |
| `std_err` | Standard error of the slope |
| `n_points` | Number of calibration points |

The slope is interpreted as sensitivity when the calibration model is appropriate and the signal and concentration units are clearly defined.

## Replicate-Aware Calibration

Real biosensor experiments often include replicate measurements at each concentration. The toolkit supports replicate-aware calibration by summarizing signals by concentration.

For each concentration, the toolkit calculates:

| Metric | Meaning |
|---|---|
| `signal_mean` | Mean signal across replicates |
| `signal_std` | Standard deviation across replicates |
| `signal_count` | Number of replicate measurements |
| `signal_rsd_percent` | Relative standard deviation in percent |

The calibration curve can then be fitted using replicate mean signals, and the replicate standard deviation can be visualized as error bars.

A typical replicate-aware workflow is:

```text
replicate measurements -> mean/SD/RSD summary -> calibration fit -> error-bar plot
```

## LOD and LOQ Estimation

The toolkit provides first-pass estimates of limit of detection (LOD) and limit of quantification (LOQ) based on blank signal variability and calibration sensitivity.

LOD is estimated as:

```text
LOD = 3 * standard deviation of blank signal / slope
```

LOQ is estimated as:

```text
LOQ = 10 * standard deviation of blank signal / slope
```

These formulas are common simple estimates, but real experimental reporting should clearly document:

- How blank samples were prepared
- How many blank replicates were measured
- Whether the calibration range is appropriate
- Whether the linear model is valid
- Whether matrix effects or electrode variability are present

## Reporting

The toolkit can generate Markdown reports for signal analysis and calibration analysis.

Signal analysis reports include:

- Feature summary
- Detected peak table
- Optional plot reference
- Notes

Calibration reports include:

- Calibration performance metrics
- Replicate summary table
- Optional calibration plot reference
- Notes

Markdown reports are lightweight, version-control friendly, and easy to convert into other formats later.

## Notebook Demonstration

The project includes a notebook demo for a full biosensor workflow. The notebook demonstrates:

- Simulated replicate measurement generation
- Replicate summary calculation
- Calibration fitting
- LOD and LOQ estimation
- Error-bar calibration plotting

The notebook is intended as a readable demonstration of the workflow rather than a replacement for the tested Python modules and example scripts.

## Assumptions and Limitations

This toolkit is currently an early-stage research-oriented project. The following limitations should be considered:

- Simulated data are simplified and do not represent all real electrochemical phenomena.
- Baseline correction currently uses a simple polynomial edge-fitting approach.
- Peak detection depends on user-selected parameters such as prominence and distance.
- LOD and LOQ estimates are first-pass calculations based on blank variability and linear calibration slope.
- Calibration assumes a linear response over the selected concentration range.
- Instrument-specific file format presets are not yet implemented.
- EIS analysis is not yet implemented.
- Experimental validation with real electrochemical datasets is still needed.

These limitations are intentional boundaries of the current version and guide future development.

## Future Improvements

Planned methodological improvements include:

- More robust baseline correction methods
- Confidence intervals for calibration curves
- Error-bar and replicate-aware plotting utilities for more workflows
- Amperometry analysis
- EIS visualization and feature extraction
- Instrument-specific import presets
- HTML or PDF report export
- Validation using real experimental biosensor datasets

## Summary

The current methodology emphasizes transparency, reproducibility, and modular analysis. Each step is designed to be inspectable:

```text
standardized data -> preprocessing -> peak detection -> feature extraction -> calibration -> reporting
```

This makes the toolkit suitable for demonstrating practical electrochemical signal analysis workflows while leaving room for more advanced methods in future versions.
