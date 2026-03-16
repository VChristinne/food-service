from fastapi import APIRouter, HTTPException, status

from Catalogue.catalogue_data import catalogue
from Catalogue.catalogue import CatalogueSchema, DishUpdateModel

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_catalogue() -> list:
    return catalogue


@router.get("/{dish_id}")
async def get_dish(dish_id: int) -> dict:
    for dish in catalogue:
        if dish["id"] == dish_id:
            return dish
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_dish(dish_data: CatalogueSchema) -> dict:
    new_dish = dish_data.model_dump()
    catalogue.append(new_dish)
    return new_dish


@router.patch("/{dish_id}")
async def update_dish(dish_id: int, dish_update_data: DishUpdateModel) -> dict:
    for dish in catalogue:
        if dish["id"] == dish_id:
            dish.update(dish_update_data.model_dump(exclude_unset=True))
            return dish
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")


@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dish(dish_id: int) -> None:
    for dish in catalogue:
        if dish["id"] == dish_id:
            catalogue.remove(dish)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
