from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.database import engine, Base
from app.models.order_model import Order
from app.config import DATABASE_URL
from app.routes.order_routes import router

print("=" * 50)
print("Connected Database:", DATABASE_URL)
print("=" * 50)

app = FastAPI(
    title="Client Data Injection Agent",
    description="FastAPI project for reading, cleaning and inserting Excel data into MySQL.",
    version="1.0.0"
)

# CORS Enable kiya (Frontend connection ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, tags=["Orders"])

# Tables Create
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")

# Frontend Static Files Mount
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")