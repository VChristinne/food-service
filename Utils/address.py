from pydantic import BaseModel
from fastapi import HTTPException
import httpx


class Address(BaseModel):
    cep: str
    state: str
    city: str
    neighborhood: str
    street: str
    number: str


async def fetch_address(cep: str) -> dict:
    cep_clean = cep.replace("-", "").strip()
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(f"https://viacep.com.br/ws/{cep_clean}/json/")

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="CEP inválido ou não encontrado")

    data = response.json()

    if "erro" in data:
        raise HTTPException(status_code=400, detail="CEP não encontrado")

    return {
        "cep": data.get("cep"),
        "state": data.get("uf"),
        "city": data.get("localidade"),
        "neighborhood": data.get("bairro"),
        "street": data.get("logradouro"),
    }
