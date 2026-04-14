from typing import TypeVar, Generic, Sequence, Type, Dict, Callable, Any
from fastapi import HTTPException, status
from sqlmodel import Session
from uuid_extensions import uuid7
from time import time

ModelT = TypeVar("ModelT")
CreateSchemaT = TypeVar("CreateSchemaT")
UpdateSchemaT = TypeVar("UpdateSchemaT")


class BaseService(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """
    Serviço genérico que implementa operações CRUD completas para qualquer modelo.
    Reduz duplicação de código entre services específicos.
    """

    def __init__(self, session: Session, repository_class: Type, model_class: Type[ModelT], model_name: str = None):
        self.repository = repository_class(session)
        self.model_class = model_class
        self.model_name = model_name or "Entity"

    # ==================== GET OPERATIONS ====================

    async def get_all(self) -> Sequence[ModelT]:
        """Retorna todas as entidades."""
        return self.repository.get_all()

    async def get_by_id(self, entity_id: str) -> ModelT:
        """Retorna uma entidade pelo ID, lançando exceção se não encontrada."""
        entity = self.repository.get_by_id(entity_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model_name} not found"
            )
        return entity

    # ==================== CREATE OPERATIONS ====================

    def create(self, entity: ModelT) -> ModelT:
        """Cria uma nova entidade."""
        return self.repository.create(entity)

    def create_from_schema(self, schema: CreateSchemaT,
                          field_transformers: Dict[str, Callable[[Any], Any]] = None) -> ModelT:
        """Cria uma entidade a partir de um schema, com transformações opcionais."""
        data = schema.model_dump()
        data["id"] = str(uuid7())

        if field_transformers:
            for field, transformer in field_transformers.items():
                if field in data:
                    data[field] = transformer(data[field])

        entity = self.model_class(**data)
        return self.repository.create(entity)

    # ==================== UPDATE OPERATIONS ====================

    def update(self, entity: ModelT) -> ModelT:
        """Atualiza uma entidade."""
        entity.updated_at = int(time())
        return self.repository.update(entity)

    async def update_by_id(self, entity_id: str, schema: UpdateSchemaT,
                          field_handlers: Dict[str, Callable] = None) -> ModelT:
        """Atualiza uma entidade pelo ID usando um schema."""
        existing = await self.get_by_id(entity_id)
        update_data = schema.model_dump(exclude_unset=True)

        # Aplica handlers customizados ou setattr padrão
        if field_handlers:
            for field, value in update_data.items():
                if field in field_handlers:
                    field_handlers[field](existing, value)
                else:
                    setattr(existing, field, value)
        else:
            # Sem handlers: aplica setattr para todos
            for field, value in update_data.items():
                setattr(existing, field, value)

        existing.updated_at = int(time())
        return self.repository.update(existing)

    # ==================== DELETE OPERATIONS ====================

    async def delete(self, entity_id: str) -> None:
        """Deleta uma entidade pelo ID."""
        await self.get_by_id(entity_id)
        self.repository.delete(entity_id)
