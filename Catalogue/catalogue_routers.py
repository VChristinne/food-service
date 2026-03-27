from typing import Sequence
from sqlmodel import Session
from fastapi import APIRouter, Depends, status, Request

from Database.db_config import db
from Catalogue.catalogue_service import CatalogueService
from Catalogue.catalogue import CatalogueSchema, CatalogueModel

router = APIRouter()


def get_catalogue_service(session: Session = Depends(db.get_session)) -> CatalogueService:
    return CatalogueService(session)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_catalogue(service: CatalogueService = Depends(get_catalogue_service)) -> Sequence[CatalogueModel]:
    return await service.get_catalogue()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_dish(request: Request, catalogue_data: CatalogueSchema, service: CatalogueService = Depends(get_catalogue_service)) -> dict:
    dish = await service.create_dish(catalogue_data, request, status.HTTP_201_CREATED)
    return {"message": "Dish created successfully", "dish": {"id": dish.id}}

@router.patch("/{dish_id}")
async def update_dish() -> dict:
    pass

@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dish() -> None:
    pass