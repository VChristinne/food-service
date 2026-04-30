from sqlmodel import Session

from Store.store import StoreModel
from Utils.base_repository import BaseRepository


class StoreRepositoy(BaseRepository[StoreModel]):
    def __init__(self, session: Session):
        super().__init__(session, StoreModel)
