

# Electrochemical Signal Analysis Toolkit

A Python toolkit for preprocessing, visualization, peak detection, feature extraction, batch analysis, calibration, and report generation for electrochemical sensing data.

This project is under active development and is designed as a research-oriented toolkit for electrochemical biosensor signal analysis.

## Motivation

Electrochemical biosensors generate signals such as cyclic voltammetry (CV), differential pulse voltammetry (DPV), amperometry, and electrochemical impedance spectroscopy (EIS). These datasets often require preprocessing, visualization, peak identification, feature extraction, calibration, and reporting before they can be interpreted or compared across experiments.

This toolkit provides a reproducible Python workflow for electrochemical signal analysis, with the current version focused on CV and DPV data.

## Current Features

- Import CSV-based electrochemical data
- Standardize potential/current column names and current units
- Generate simulated CV and DPV datasets
- Smooth current signals using Savitzky-Golay filtering
- Apply polynomial baseline correction
- Detect oxidation and reduction peaks
- Extract CV and DPV signal features
- Analyze individual CV and DPV files
- Run batch analysis for multiple CV or DPV files
- Build calibration curves from concentration-response data
- Estimate limit of detection from blank measurements
- Generate plots and Markdown analysis reports
- Provide example scripts and test coverage
- Perform replicate-aware calibration analysis
- Calculate replicate mean, standard deviation, count, and RSD
- Estimate both LOD and LOQ from blank measurements
- Plot calibration curves with error bars
- Generate Markdown calibration reports
- Provide a notebook demo for the full biosensor workflow

## Example Workflows
```markdown
For details on the analysis workflow and methodological assumptions, see [Methodology](docs/methodology.md).

### Single CV Analysis

```text
CV data -> preprocessing -> peak detection -> feature extraction -> report
```

### Single DPV Analysis

```text
DPV data -> preprocessing -> peak detection -> feature extraction -> report
```

### Batch CV Calibration

```text
multiple CV files -> batch summary -> calibration curve -> LOD estimate
```

### Batch DPV Calibration

```text
multiple DPV files -> batch summary -> calibration curve -> LOD estimate
```

### Replicate-Aware Calibration

```text
replicate measurements -> mean/SD/RSD summary -> calibration fit -> LOD/LOQ -> report
```

### Full Biosensor Workflow Demo

```text
simulated biosensor replicates -> calibration summary -> error-bar plot -> Markdown report -> notebook demo
```


## Project Structure

```text
electrochemical-signal-analysis-toolkit/
├── data/
│   ├── processed/
│   └── raw/
├── docs/
├── examples/
│   ├── __init__.py
│   ├── basic_cv_analysis.py
│   ├── basic_dpv_analysis.py
│   ├── batch_cv_analysis.py
│   ├── batch_dpv_analysis.py
│   ├── batch_to_calibration.py
│   ├── batch_dpv_to_calibration.py
│   ├── calibration_analysis.py
│   ├── replicate_calibration_analysis.py
│   ├── full_biosensor_workflow.py
│   └── create_demo_notebook.py
├── learning-notes/
│   └── cv-and-dpv-basics.md
├── notebooks/
│   └── demo_biosensor_workflow.ipynb
├── src/
│   └── echem_signal_toolkit/
│       ├── __init__.py
│       ├── batch.py
│       ├── calibration.py
│       ├── dpv.py
│       ├── features.py
│       ├── io.py
│       ├── peaks.py
│       ├── plotting.py
│       ├── preprocessing.py
│       ├── report.py
│       └── simulation.py
├── tests/
├── LICENSE
├── README.md
├── pyproject.toml
└── requirements.txt
```

## Installation

Clone the repository:

```bash
git clone https://github.com/mutangoao-art/electrochemical-signal-analysis-toolkit.git
cd electrochemical-signal-analysis-toolkit
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the package in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

## Quick Start

Run the CV example:

```bash
python3 examples/basic_cv_analysis.py
```

Run the DPV example:

```bash
python3 examples/basic_dpv_analysis.py
```

Run batch CV analysis:

```bash
python3 examples/batch_cv_analysis.py
```

Run batch DPV analysis:

```bash
python3 examples/batch_dpv_analysis.py
```

Run calibration examples:

```bash
python3 examples/calibration_analysis.py
python3 examples/batch_to_calibration.py
python3 examples/batch_dpv_to_calibration.py
```

Run replicate calibration analysis:

```bash
python3 examples/replicate_calibration_analysis.py

Run the full biosensor workflow:

```bash
python3 examples/full_biosensor_workflow.py

Generate the demo notebook:

```bash
python3 examples/create_demo_notebook.py


## Example Python Usage

```python
from echem_signal_toolkit.io import load_cv_data
from echem_signal_toolkit.preprocessing import smooth_current, baseline_correct_current
from echem_signal_toolkit.peaks import detect_cv_peaks
from echem_signal_toolkit.features import extract_cv_features

data = load_cv_data("data/raw/simulated_cv.csv")

processed = smooth_current(data)
processed = baseline_correct_current(
    processed,
    current_col="current_smoothed_a",
)

peaks = detect_cv_peaks(
    processed,
    current_col="current_corrected_a",
    prominence=0.5e-6,
)

features = extract_cv_features(
    processed,
    peaks,
    current_col="current_corrected_a",
)

print(features)
```

## Standardized Data Format

Internally, electrochemical data are standardized to the following column names:

| Column | Description |
|---|---|
| `potential_v` | Applied potential in volts |
| `current_a` | Measured current in amperes |
| `time_s` | Time in seconds, if available |
| `cycle` | Cycle or segment number, if available |

The import functions support explicit column mapping and current unit conversion.

## Simulated Data

The project includes simulated CV and DPV data generators for testing and demonstration.

Simulated CV data include:

- Triangular potential sweep
- Background current
- Oxidation and reduction peaks
- Gaussian noise

Simulated DPV data include:

- Linear potential sweep
- Background current
- Main oxidation peak
- Gaussian noise

These simulated datasets allow the full workflow to run without experimental data.

## Testing

Run the test suite:

```bash
python3 -m pytest
```

The test suite covers data import, simulation, preprocessing, peak detection, feature extraction, calibration, batch analysis, report generation, and the full workflow helper.

## Development Status

This project is in early active development. The current version focuses on reproducible CV and DPV signal analysis workflows for electrochemical biosensor data.

## Roadmap

Planned improvements include:

- Calibration plots with confidence intervals
- More advanced baseline correction methods
- Amperometry analysis
- EIS visualization and feature extraction
- Compatibility presets for common instrument export formats
- HTML or PDF report export

## Research Context

This project is motivated by electrochemical biosensor data analysis workflows, where reproducible preprocessing, peak extraction, calibration, and reporting are important for evaluating sensor performance across samples and analyte concentrations.

## License

This project is licensed under the terms of the included LICENSE file.
