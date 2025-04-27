
from fastapi import FastAPI
from app.api import users
from core.database import Base, engine

def create_tables():
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Water Billing System Api",
    description="API for managing water billing systems",
    security=[{"bearerAuth": []}]
)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    create_tables()

app.include_router(users.router)