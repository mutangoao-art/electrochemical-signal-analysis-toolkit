from __future__ import annotations

from pathlib import Path

import nbformat as nbf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "demo_biosensor_workflow.ipynb"


def main() -> None:
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)

    nb = nbf.v4.new_notebook()

    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# Demo Biosensor Workflow\n\n"
            "This notebook demonstrates a replicate-aware calibration workflow "
            "for simulated electrochemical biosensor data."
        ),
        nbf.v4.new_markdown_cell(
            "## Workflow\n\n"
            "The workflow includes:\n\n"
            "1. Generate simulated replicate measurements\n"
            "2. Summarize replicate signals by concentration\n"
            "3. Fit a calibration curve\n"
            "4. Estimate LOD and LOQ\n"
            "5. Plot the calibration curve with error bars"
        ),
        nbf.v4.new_code_cell(
            "import pandas as pd\n"
            "from examples.full_biosensor_workflow import generate_biosensor_replicates\n"
            "from echem_signal_toolkit.calibration import (\n"
            "    calibration_performance_summary,\n"
            "    estimate_lod,\n"
            "    estimate_loq,\n"
            "    fit_replicate_calibration_curve,\n"
            "    summarize_replicates,\n"
            ")\n"
            "from echem_signal_toolkit.plotting import plot_replicate_calibration_curve"
        ),
        nbf.v4.new_markdown_cell("## Generate Simulated Replicate Data"),
        nbf.v4.new_code_cell(
            "measurements = generate_biosensor_replicates()\n"
            "measurements.head()"
        ),
        nbf.v4.new_markdown_cell("## Summarize Replicates"),
        nbf.v4.new_code_cell(
            "replicate_summary = summarize_replicates(measurements)\n"
            "replicate_summary"
        ),
        nbf.v4.new_markdown_cell("## Fit Calibration Curve"),
        nbf.v4.new_code_cell(
            "fit_result = fit_replicate_calibration_curve(replicate_summary)\n"
            "fit_result"
        ),
        nbf.v4.new_markdown_cell("## Estimate LOD and LOQ"),
        nbf.v4.new_code_cell(
            "blank_signals = measurements.loc[\n"
            "    measurements['concentration'] == 0.0,\n"
            "    'signal',\n"
            "]\n\n"
            "lod = estimate_lod(blank_signals, slope=fit_result['slope'])\n"
            "loq = estimate_loq(blank_signals, slope=fit_result['slope'])\n\n"
            "performance = calibration_performance_summary(\n"
            "    fit_result=fit_result,\n"
            "    lod=lod,\n"
            "    loq=loq,\n"
            "    concentration_unit='uM',\n"
            "    signal_unit='A',\n"
            ")\n\n"
            "pd.DataFrame([performance])"
        ),
        nbf.v4.new_markdown_cell("## Plot Calibration Curve"),
        nbf.v4.new_code_cell(
            "plot_replicate_calibration_curve(\n"
            "    replicate_summary,\n"
            "    fit_result,\n"
            "    title='Simulated Biosensor Calibration',\n"
            "    concentration_unit='uM',\n"
            "    signal_unit='A',\n"
            ");"
        ),
    ]

    nbf.write(nb, NOTEBOOK_PATH)
    print(f"Notebook created: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()