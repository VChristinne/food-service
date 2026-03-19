from typing import Sequence
from sqlmodel import Session, select

from Client.client import ClientModel


class ClientRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, client: ClientModel) -> ClientModel:
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

    def get_all(self) -> Sequence[ClientModel]:
        return self.session.exec(select(ClientModel)).all()

    def get_by_id(self, client_id: str) -> ClientModel | None:
        return self.session.get(ClientModel, client_id)

    def delete(self, client_id: str) -> None:
        client = self.get_by_id(client_id)
        if client:
            self.session.delete(client)
            self.session.commit()
        else:
            raise ValueError(f"Client with id {client_id} not found")
