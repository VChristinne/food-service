from fastapi import APIRouter, status

from Client.client import ClientSchema
from Client.client_data import clients
from Utils.address import fetch_address

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_clients() -> list:
    return clients


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_client(client_data: ClientSchema) -> dict:
    address = await fetch_address(client_data.cep)
    address["complement"] = client_data.complement

    new_client = {
        "name": client_data.name,
        "email": client_data.email,
        "phone": client_data.phone,
        "address": address,
    }
    clients.append(new_client)
    return {"message": "Client created successfully", "client": new_client}
