
import pandas as pd
from pathlib import Path

def read_excel(file_path: Path) -> list[dict]:
    """
    Read an Excel file and return a list of row dictionaries.
    Keys are column headers, values are cell values.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    df = pd.read_excel(file_path)

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Strip whitespace from string values
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    # Drop completely empty rows
    df = df.dropna(how="all")

    return df.to_dict(orient="records")