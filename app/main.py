from fastapi import FastAPI

from app.database import engine, Base
from app.models.order_model import Order
from app.config import DATABASE_URL
from app.routes.order_routes import router

# Print the database URL
print("=" * 50)
print("Connected Database:", DATABASE_URL)
print("=" * 50)

app = FastAPI(
    title="Client Data Injection Agent",
    description="FastAPI project for reading, cleaning and inserting Excel data into MySQL.",
    version="1.0.0"
)

app.include_router(router, tags=["Orders"])

# Check which tables SQLAlchemy knows about
print("Tables before create_all():", Base.metadata.tables.keys())

# Create tables
Base.metadata.create_all(bind=engine)

# Check tables again
print("Tables after create_all():", Base.metadata.tables.keys())

print("✅ Tables created successfully!")

@app.get("/")
def home():
    return {
        "message": "Client Data Injection Agent is Running Successfully!"
    }