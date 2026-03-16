from fastapi import FastAPI
from Client.client_routers import router as client_router
from Catalogue.catalogue_routers import router as catalogue_router


version = "v1"

app = FastAPI(
    title="Food Service API",
    description="A RESTful API for managing a food service application.",
    version=version,
)

app.include_router(client_router, prefix=f"/api/{version}/clients", tags=["clients"])
# app.include_router(employee_router, prefix=f"/api/{version}/employees", tags=["employees"])
app.include_router(catalogue_router, prefix=f"/api/{version}/catalogue", tags=["catalogue"])
