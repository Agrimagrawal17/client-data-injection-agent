from sqlalchemy.orm import Session

from app.models.order_model import Order



# SAVE ORDERS

def save_orders(df, db: Session):

    inserted = 0
    duplicates = 0
    failed = 0

    for _, row in df.iterrows():

        order_id = int(row["order_id"])

        existing_order = (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )

        if existing_order:
            duplicates += 1
            continue

        try:

            order = Order(
                order_id=order_id,

                date=row["date"].date()
                if pd_not_null(row["date"])
                else None,

                customer_name=row["customer_name"],
                customer_age=int(row["customer_age"]),
                product=row["product"],
                category=row["category"],
                price=float(row["price"]),
                quantity=int(row["quantity"]),
                total_sales=float(row["total_sales"]),
                discount=int(row["discount_(%)"]),
                final_sales=float(row["final_sales"]),
                region=row["region"],
                payment_method=row["payment_method"],
                delivery_status=row["delivery_status"]
            )

            db.add(order)
            inserted += 1

        except Exception as e:

            print("ERROR INSERTING ORDER:", e)

            db.rollback()
            failed += 1

    db.commit()

    return {
        "inserted": inserted,
        "duplicates": duplicates,
        "failed": failed
    }



# GET ALL ORDERS


def get_all_orders(db: Session):

    orders = (
        db.query(Order)
        .all()
    )

    return orders



# GET ORDERS IN CHUNKS


def get_orders_chunk(
    db: Session,
    skip: int = 0,
    limit: int = 50
):

    orders = (
        db.query(Order)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return orders


# ADVANCED / CUSTOM FILTER ORDERS

def filter_orders(
    db: Session,

    # Text filters
    region: str = None,
    category: str = None,
    payment_method: str = None,
    delivery_status: str = None,

    # Age filters
    min_age: int = None,
    max_age: int = None,

    # Price filters
    min_price: float = None,
    max_price: float = None,

    # Final sales filters
    min_final_sales: float = None,
    max_final_sales: float = None,

    # Date filters
    start_date: str = None,
    end_date: str = None,

    # Sorting
    sort_by: str = None,
    sort_order: str = "asc",

    # Pagination
    skip: int = 0,
    limit: int = 50
):

    # Start query
    query = db.query(Order)

    # TEXT FILTERS

    if region:

        query = query.filter(
            Order.region == region
        )

    if category:

        query = query.filter(
            Order.category == category
        )

    if payment_method:

        query = query.filter(
            Order.payment_method == payment_method
        )

    if delivery_status:

        query = query.filter(
            Order.delivery_status == delivery_status
        )

    # AGE FILTERS

    if min_age is not None:

        query = query.filter(
            Order.customer_age >= min_age
        )

    if max_age is not None:

        query = query.filter(
            Order.customer_age <= max_age
        )

    # PRICE FILTERS

    if min_price is not None:

        query = query.filter(
            Order.price >= min_price
        )

    if max_price is not None:

        query = query.filter(
            Order.price <= max_price
        )

    # FINAL SALES FILTERS

    if min_final_sales is not None:

        query = query.filter(
            Order.final_sales >= min_final_sales
        )

    if max_final_sales is not None:

        query = query.filter(
            Order.final_sales <= max_final_sales
        )

    # DATE FILTERS

    if start_date:

        query = query.filter(
            Order.date >= start_date
        )

    if end_date:

        query = query.filter(
            Order.date <= end_date
        )

    # SORTING

    allowed_sort_fields = {

        "price": Order.price,

        "customer_age": Order.customer_age,

        "quantity": Order.quantity,

        "total_sales": Order.total_sales,

        "final_sales": Order.final_sales,

        "order_id": Order.order_id,

        "date": Order.date
    }

    if sort_by in allowed_sort_fields:

        column = allowed_sort_fields[sort_by]

        if sort_order.lower() == "desc":

            query = query.order_by(
                column.desc()
            )

        else:

            query = query.order_by(
                column.asc()
            )

    # PAGINATION

    query = (
        query
        .offset(skip)
        .limit(limit)
    )

    # Execute query
    return query.all()


# DATE NULL CHECK

def pd_not_null(value):

    try:

        import pandas as pd

        return not pd.isna(value)

    except Exception:

        return value is not None