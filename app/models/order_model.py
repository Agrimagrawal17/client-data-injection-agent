from sqlalchemy import Column, Integer, String, Float, Date
from app.database import Base


class Order(Base):

    __tablename__ = "orders"

    # Primary Key
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Order Information
    order_id = Column(
        Integer,
        unique=True,
        nullable=False
    )

    date = Column(Date)

    customer_name = Column(String(100))

    customer_age = Column(Integer)

    product = Column(String(100))

    category = Column(String(100))

    price = Column(Float)

    quantity = Column(Integer)

    total_sales = Column(Float)

    discount = Column(Integer)

    final_sales = Column(Float)

    region = Column(String(50))

    payment_method = Column(String(50))

    delivery_status = Column(String(50))