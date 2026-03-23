from typing import Sequence
from sqlmodel import Session
from uuid_extensions import uuid7

from Audit.audit import AuditActionEnum
from Audit.audit_service import AuditService
from Client.client import ClientSchema, ClientModel
from Client.client_repository import ClientRepository
from Utils.address import fetch_address
from Utils.validations import hash_password


class ClientService:
    def __init__(self, session: Session):
        self.repository = ClientRepository(session)
        self.audit_service = AuditService(session)

    async def get_clients(self) -> Sequence[ClientModel]:
        return self.repository.get_all()

    async def create_client(self, client_data: ClientSchema) -> ClientModel:
        address = await fetch_address(client_data.cep)
        address["complement"] = client_data.complement

        client = ClientModel(
            id=str(uuid7()),
            name=client_data.name,
            password_hash=hash_password(client_data.password),
            email=client_data.email,
            phone=client_data.phone,
            address=address
        )
        created_client = self.repository.create(client)

        self.audit_service.log(
            action=AuditActionEnum.CREATE,
            entity="client",
            entity_id=created_client.id,
            user_id=created_client.id  # TODO: Change to jwt when implemented
        )
        return created_client
