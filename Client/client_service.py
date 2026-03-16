from typing import Sequence
from uuid import uuid7
from sqlmodel import Session

from Client.client import ClientSchema, ClientModel
from Client.client_repository import ClientRepository
from Utils.address import fetch_address
from Utils.validations import hash_password


class ClientService:
    def __init__(self, session: Session):
        self.repository = ClientRepository(session)

    async def create_client(self, client_data: ClientSchema) -> ClientModel:
        address = await fetch_address(client_data.cep)
        address["complement"] = client_data.complement

        client = ClientModel(
            id=str(uuid7()),
            name=client_data.name,
            password_hash=hash_password(client_data.password),
            email=client_data.email,
            phone=client_data.phone,
            address=address,
        )
        return self.repository.create(client)

    async def get_clients(self) -> Sequence[ClientModel]:
        return self.repository.get_all()
