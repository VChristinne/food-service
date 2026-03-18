from fastapi import FastAPI

from Database.db_config import db
from Client.client_routers import router as client_router
from Inventory.inventory_routers import router as inventory_router
from Catalogue.catalogue_routers import router as catalogue_router


version = "v1"

app = FastAPI(
    title="Food Service API",
    description="A RESTful API for managing a food service application.",
    version=version,
)

db.create_tables()

app.include_router(client_router, prefix=f"/api/{version}/clients", tags=["clients"])
app.include_router(inventory_router, prefix=f"/api/{version}/inventory", tags=["inventory"])
app.include_router(catalogue_router, prefix=f"/api/{version}/catalogue", tags=["catalogue"])
