from typing import Sequence
from sqlmodel import Session
from fastapi import APIRouter, Depends, status

from Database.db_config import db
from Inventory.inventory_service import InventoryService
from Inventory.inventory import InventorySchema, InventoryModel

router = APIRouter()


def get_inventory_service(session: Session = Depends(db.get_session)) -> InventoryService:
    return InventoryService(session)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_inventory(service: InventoryService = Depends(get_inventory_service)) -> Sequence[InventoryModel]:
    return await service.get_inventory()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(item_data: InventorySchema, service: InventoryService = Depends(get_inventory_service)) -> dict:
    item = await service.create_item(item_data)
    return {"message": "Item created successfully", "item": item}

@router.put("/{item_id}", status_code=status.HTTP_200_OK)
async def update_item(item_id: str, item_data: InventorySchema, service: InventoryService = Depends(get_inventory_service)) -> dict:
    await service.update_inventory(item_id, item_data)
    return {"message": "Item updated successfully", "item_id": item_id}

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str, service: InventoryService = Depends(get_inventory_service)) -> None:
    await service.delete_item(item_id)
