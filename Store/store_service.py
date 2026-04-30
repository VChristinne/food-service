from sqlmodel import Session

from Store.store import StoreModel, StoreSchema, StoreUpdateSchema
from Store.store_repository import StoreRepositoy
from Utils.base_service import BaseService
from Utils.address import fetch_address


async def _handle_cep(entity: StoreModel, cep: str) -> None:
    address = await fetch_address(cep)
    address["complement"] = entity.address.get("complement")
    entity.address = address


class StoreService(BaseService[StoreModel, StoreSchema, StoreUpdateSchema]):
    def __init__(self, session: Session):
        super().__init__(session, StoreRepositoy, StoreModel, "Store")

    async def create_store(self, store_data: StoreSchema) -> StoreModel:
        address = await fetch_address(store_data.cep)
        address["complement"] = store_data.complement

        store = StoreModel(
            phone=store_data.phone,
            address=address
        )
        return self.create(store)

    async def update_store(self, store_id: str, store_data: StoreUpdateSchema) -> StoreModel:
        return await self.update_by_id(
            store_id,
            store_data,
            field_handlers={
                "cep": _handle_cep,
            }
        )

