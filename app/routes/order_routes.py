from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.excel_service import process_excel

import shutil
import os

from app.repository.order_repository import (
    get_all_orders,
    get_orders_chunk,
    filter_orders
)



router = APIRouter()

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# 1. UPLOAD EXCEL / CSV

@router.post("/upload-excel")
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Validate file type

    if not file.filename.lower().endswith(
        (".csv", ".xlsx", ".xls")
    ):
        return {
            "error": "Only CSV, XLSX and XLS files are allowed."
        }

    # Save uploaded file

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # Process + Clean + Insert into Database

    result = process_excel(
        file_path,
        db
    )

    # Response

    return {
        "message": "File uploaded and processed successfully.",

        "original_rows": result["original_rows"],

        "cleaned_rows": result["cleaned_rows"],

        "inserted_records": result["inserted_records"],

        "duplicate_records": result["duplicate_records"],

        "failed_records": result["failed_records"],

        "columns": result["columns"],

        "remaining_null_values": result["null_values"]
    }


# 2. GET ALL ORDERS

@router.get("/orders")
def get_orders(
    db: Session = Depends(get_db)
):

    orders = get_all_orders(db)

    return {
        "total_records": len(orders),

        "data": [
            {
                "id": order.id,
                "order_id": order.order_id,
                "date": order.date,
                "customer_name": order.customer_name,
                "customer_age": order.customer_age,
                "product": order.product,
                "category": order.category,
                "price": order.price,
                "quantity": order.quantity,
                "total_sales": order.total_sales,
                "discount": order.discount,
                "final_sales": order.final_sales,
                "region": order.region,
                "payment_method": order.payment_method,
                "delivery_status": order.delivery_status
            }

            for order in orders
        ]
    }


# 3. GET ORDERS IN CHUNKS / PAGINATION

@router.get("/orders/chunk")
def get_orders_chunk_api(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):

    # Basic validation

    if skip < 0:
        return {
            "error": "skip cannot be negative."
        }

    if limit <= 0:
        return {
            "error": "limit must be greater than 0."
        }

    # Fetch records from database

    orders = get_orders_chunk(
        db=db,
        skip=skip,
        limit=limit
    )

    # Return response

    return {
        "skip": skip,

        "limit": limit,

        "records_returned": len(orders),

        "data": [
            {
                "id": order.id,
                "order_id": order.order_id,
                "date": order.date,
                "customer_name": order.customer_name,
                "customer_age": order.customer_age,
                "product": order.product,
                "category": order.category,
                "price": order.price,
                "quantity": order.quantity,
                "total_sales": order.total_sales,
                "discount": order.discount,
                "final_sales": order.final_sales,
                "region": order.region,
                "payment_method": order.payment_method,
                "delivery_status": order.delivery_status
            }

            for order in orders
        ]
    }
    
# 4. FILTER ORDERS

@router.get("/orders/filter")
def filter_orders_api(
    region: str = None,
    category: str = None,
    payment_method: str = None,
    delivery_status: str = None,

    min_age: int = None,
    max_age: int = None,

    min_price: float = None,
    max_price: float = None,

    min_final_sales: float = None,
    max_final_sales: float = None,

    start_date: str = None,
    end_date: str = None,

    sort_by: str = None,
    sort_order: str = "asc",

    db: Session = Depends(get_db)
):

    orders = filter_orders(
        db=db,

        region=region,
        category=category,
        payment_method=payment_method,
        delivery_status=delivery_status,

        min_age=min_age,
        max_age=max_age,

        min_price=min_price,
        max_price=max_price,

        min_final_sales=min_final_sales,
        max_final_sales=max_final_sales,

        start_date=start_date,
        end_date=end_date,

        sort_by=sort_by,
        sort_order=sort_order
    )

    return {
        "filters": {
            "region": region,
            "category": category,
            "payment_method": payment_method,
            "delivery_status": delivery_status,

            "min_age": min_age,
            "max_age": max_age,

            "min_price": min_price,
            "max_price": max_price,

            "min_final_sales": min_final_sales,
            "max_final_sales": max_final_sales,

            "start_date": start_date,
            "end_date": end_date,

            "sort_by": sort_by,
            "sort_order": sort_order
        },

        "records_found": len(orders),

        "data": [
            {
                "id": order.id,
                "order_id": order.order_id,
                "date": order.date,
                "customer_name": order.customer_name,
                "customer_age": order.customer_age,
                "product": order.product,
                "category": order.category,
                "price": order.price,
                "quantity": order.quantity,
                "total_sales": order.total_sales,
                "discount": order.discount,
                "final_sales": order.final_sales,
                "region": order.region,
                "payment_method": order.payment_method,
                "delivery_status": order.delivery_status
            }
            for order in orders
        ]
    }