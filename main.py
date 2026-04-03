from fastapi import FastAPI
from sqlmodel import Session

from Database.db_config import db
from Audit.audit_service import AuditService
from Audit.audit_middleware import AuditMiddleware
from Audit.audit_decorator import AuditDecorator

version = "v1"

db.create_tables()
session = Session(db.engine)
audit_service = AuditService(session)
audit_decorator = AuditDecorator(audit_service)

app = FastAPI(
    title="Food Service API",
    description="A RESTful API for managing a food service application.",
    version=version,
)

app.add_middleware(AuditMiddleware, audit_service=audit_service)

from Costumer.costumer_routers import router as client_router
from Inventory.inventory_routers import router as inventory_router
from Catalogue.catalogue_routers import router as catalogue_router
from Auth.auth_routers import router as auth_router

app.include_router(client_router, prefix=f"/api/{version}/costumers", tags=["costumers"])
app.include_router(inventory_router, prefix=f"/api/{version}/inventory", tags=["inventory"])
app.include_router(catalogue_router, prefix=f"/api/{version}/catalogue", tags=["catalogue"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])