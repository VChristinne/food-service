from sqlmodel import Session

from Catalogue.catalogue import CatalogueModel
from Utils.base_repository import BaseRepository


class CatalogueRepository(BaseRepository[CatalogueModel]):
    def __init__(self, session: Session):
        super().__init__(session, CatalogueModel)
