from __future__ import annotations

from pathlib import Path

import pandas as pd


STANDARD_COLUMNS = {
    "potential": "potential_v",
    "potential_v": "potential_v",
    "potential (v)": "potential_v",
    "e/v": "potential_v",
    "voltage": "potential_v",
    "voltage_v": "potential_v",
    "current": "current_a",
    "current_a": "current_a",
    "current (a)": "current_a",
    "i/a": "current_a",
    "time": "time_s",
    "time_s": "time_s",
    "time (s)": "time_s",
    "cycle": "cycle",
    "cycle_number": "cycle",
    "segment": "cycle",
}


CURRENT_UNIT_SCALE = {
    "a": 1.0,
    "ma": 1e-3,
    "ua": 1e-6,
    "µa": 1e-6,
    "na": 1e-9,
}


def read_csv_data(
    file_path: str | Path,
    *,
    delimiter: str | None = None,
    skiprows: int = 0,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    """
    Read electrochemical data from a CSV or delimited text file.

    Parameters
    ----------
    file_path:
        Path to the input data file.
    delimiter:
        Column delimiter. If None, pandas will try to infer it.
    skiprows:
        Number of rows to skip at the beginning of the file.
    encoding:
        File encoding.

    Returns
    -------
    pandas.DataFrame
        Raw imported dataframe.
    """
    file_path = Path(file_path)

    if delimiter is None:
        return pd.read_csv(file_path, sep=None, engine="python", skiprows=skiprows, encoding=encoding)

    return pd.read_csv(file_path, sep=delimiter, skiprows=skiprows, encoding=encoding)


def standardize_cv_dataframe(
    df: pd.DataFrame,
    *,
    potential_col: str | None = None,
    current_col: str | None = None,
    time_col: str | None = None,
    cycle_col: str | None = None,
    current_unit: str = "A",
) -> pd.DataFrame:
    """
    Standardize cyclic voltammetry data to internal column names.

    The returned dataframe uses:

    - potential_v
    - current_a
    - time_s, if available
    - cycle, if available

    Parameters
    ----------
    df:
        Raw dataframe.
    potential_col:
        Name of the potential column in the raw dataframe.
    current_col:
        Name of the current column in the raw dataframe.
    time_col:
        Optional time column.
    cycle_col:
        Optional cycle or segment column.
    current_unit:
        Unit of the current column: A, mA, uA, µA, or nA.

    Returns
    -------
    pandas.DataFrame
        Standardized CV dataframe.
    """
    standardized = df.copy()

    column_map = _infer_column_map(
        standardized,
        potential_col=potential_col,
        current_col=current_col,
        time_col=time_col,
        cycle_col=cycle_col,
    )

    standardized = standardized.rename(columns=column_map)

    required_columns = {"potential_v", "current_a"}
    missing = required_columns.difference(standardized.columns)

    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Missing required standardized column(s): {missing_text}")

    scale = _current_scale(current_unit)
    standardized["current_a"] = pd.to_numeric(standardized["current_a"], errors="coerce") * scale
    standardized["potential_v"] = pd.to_numeric(standardized["potential_v"], errors="coerce")

    if "time_s" in standardized.columns:
        standardized["time_s"] = pd.to_numeric(standardized["time_s"], errors="coerce")

    if "cycle" in standardized.columns:
        standardized["cycle"] = pd.to_numeric(standardized["cycle"], errors="coerce").astype("Int64")

    output_columns = ["potential_v", "current_a"]

    if "time_s" in standardized.columns:
        output_columns.append("time_s")

    if "cycle" in standardized.columns:
        output_columns.append("cycle")

    standardized = standardized[output_columns].dropna(subset=["potential_v", "current_a"])
    standardized = standardized.reset_index(drop=True)

    return standardized


def load_cv_data(
    file_path: str | Path,
    *,
    delimiter: str | None = None,
    skiprows: int = 0,
    encoding: str = "utf-8",
    potential_col: str | None = None,
    current_col: str | None = None,
    time_col: str | None = None,
    cycle_col: str | None = None,
    current_unit: str = "A",
) -> pd.DataFrame:
    """
    Read and standardize cyclic voltammetry data in one step.
    """
    raw_df = read_csv_data(
        file_path,
        delimiter=delimiter,
        skiprows=skiprows,
        encoding=encoding,
    )

    return standardize_cv_dataframe(
        raw_df,
        potential_col=potential_col,
        current_col=current_col,
        time_col=time_col,
        cycle_col=cycle_col,
        current_unit=current_unit,
    )


def _infer_column_map(
    df: pd.DataFrame,
    *,
    potential_col: str | None,
    current_col: str | None,
    time_col: str | None,
    cycle_col: str | None,
) -> dict[str, str]:
    explicit_map = {
        potential_col: "potential_v",
        current_col: "current_a",
        time_col: "time_s",
        cycle_col: "cycle",
    }

    column_map = {
        raw_col: standard_col
        for raw_col, standard_col in explicit_map.items()
        if raw_col is not None
    }

    for column in df.columns:
        normalized = str(column).strip().lower()

        if normalized in STANDARD_COLUMNS and column not in column_map:
            column_map[column] = STANDARD_COLUMNS[normalized]

    return column_map


def _current_scale(current_unit: str) -> float:
    normalized_unit = current_unit.strip().lower()

    if normalized_unit not in CURRENT_UNIT_SCALE:
        allowed = ", ".join(CURRENT_UNIT_SCALE)
        raise ValueError(f"Unsupported current unit: {current_unit}. Allowed units: {allowed}")

    return CURRENT_UNIT_SCALE[normalized_unit]

def read_chi_amperometry_data(
    file_path: str | Path,
    *,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    """
    Read CH Instruments amperometric i-t data.

    The function searches for the data header line starting with 'Time/s'
    and returns standardized columns such as:
    - time_s
    - i4_a
    - i6_a
    - i8_a
    """
    file_path = Path(file_path)
    lines = file_path.read_text(encoding=encoding).splitlines()

    header_index = None

    for index, line in enumerate(lines):
        if line.strip().lower().startswith("time/s"):
            header_index = index
            break

    if header_index is None:
        raise ValueError("Could not find amperometry data header starting with 'Time/s'")

    raw = pd.read_csv(
        file_path,
        skiprows=header_index,
        sep=",",
        engine="python",
        encoding=encoding,
    )

    raw.columns = [str(column).strip() for column in raw.columns]

    column_map = {}

    for column in raw.columns:
        normalized = column.strip().lower()

        if normalized == "time/s":
            column_map[column] = "time_s"
        elif normalized.startswith("i") and normalized.endswith("/a"):
            channel = normalized.replace("/a", "").replace(" ", "")
            column_map[column] = f"{channel}_a"

    standardized = raw.rename(columns=column_map)

    for column in standardized.columns:
        standardized[column] = pd.to_numeric(standardized[column], errors="coerce")

    standardized = standardized.dropna(subset=["time_s"]).reset_index(drop=True)

    return standardized