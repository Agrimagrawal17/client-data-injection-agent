import os
import pandas as pd


def clean_excel_data(file_path: str):

    # 1. Detect file type

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".csv":
        df = pd.read_csv(file_path)

    elif extension == ".xlsx":
        df = pd.read_excel(file_path, engine="openpyxl")

    elif extension == ".xls":
        df = pd.read_excel(file_path, engine="xlrd")

    else:
        raise ValueError(
            "Unsupported file format. "
            "Only .csv, .xlsx and .xls files are allowed."
        )

    # 2. Original row count

    original_rows = len(df)

    # 3. Clean column names

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # 4. Check order_id column

    if "order_id" not in df.columns:
        raise ValueError(
            "Required column 'order_id' is missing from the file."
        )

    # 5. Convert order_id to numeric

    df["order_id"] = pd.to_numeric(
        df["order_id"],
        errors="coerce"
    )

    # 6. Remove rows with missing order_id

    df = df.dropna(subset=["order_id"])

    # Convert order_id to integer
    df["order_id"] = df["order_id"].astype(int)

    # 7. Remove duplicate order_id values

    df = df.drop_duplicates(
        subset=["order_id"],
        keep="first"
    )

    # 8. Remove complete duplicate rows

    df = df.drop_duplicates()

    # 9. Fill missing string values

    string_columns = df.select_dtypes(
        include=["object"]
    ).columns

    for col in string_columns:
        df[col] = df[col].fillna("Unknown")

    # 10. Fill missing numeric values

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns

    for col in numeric_columns:

        # IMPORTANT:
        # order_id is NOT filled with 0
        if col != "order_id":
            df[col] = df[col].fillna(0)

    # 11. Convert date

    if "date" in df.columns:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    # 12. Remaining null values

    remaining_null_values = int(
        df.isnull().sum().sum()
    )

    # 13. Return result

    return {
        "dataframe": df,
        "original_rows": original_rows,
        "cleaned_rows": len(df),
        "columns": list(df.columns),
        "null_values": remaining_null_values
    }