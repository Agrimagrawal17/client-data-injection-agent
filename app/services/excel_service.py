from sqlalchemy.orm import Session

from app.utils.clean_data import clean_excel_data
from app.repository.order_repository import save_orders


def process_excel(file_path: str, db: Session):

    # Clean the uploaded file
    result = clean_excel_data(file_path)

    # Insert cleaned data into database
    database_result = save_orders(
        result["dataframe"],
        db
    )

    return {
        "original_rows": result["original_rows"],
        "cleaned_rows": result["cleaned_rows"],
        "columns": result["columns"],
        "null_values": result["null_values"],
        "inserted_records": database_result["inserted"],
        "duplicate_records": database_result["duplicates"],
        "failed_records": database_result["failed"]
    }