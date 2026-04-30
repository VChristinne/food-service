from typing import TypeVar, Generic, Sequence, Type, Dict, Callable, Any
from fastapi import HTTPException, status
from sqlmodel import Session
from uuid_extensions import uuid7
from time import time
from math import ceil

ModelT = TypeVar("ModelT")
CreateSchemaT = TypeVar("CreateSchemaT")
UpdateSchemaT = TypeVar("UpdateSchemaT")


class BaseService(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """
    Generic service to handle CRUD operations for any entity type, using a repository pattern.
    """

    def __init__(self, session: Session, repository_class: Type, model_class: Type[ModelT], model_name: str = None):
        self.repository = repository_class(session)
        self.model_class = model_class
        self.model_name = model_name or "Entity"

    # ==================== GET OPERATIONS ====================

    async def get_all(self) -> Sequence[ModelT]:
        """Return any entities."""
        return self.repository.get_all()

    async def get_by_id(self, entity_id: str) -> ModelT:
        """Return an entity by ID, or raise 404 if not found."""
        entity = self.repository.get_by_id(entity_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model_name} not found"
            )
        return entity

    # ==================== CREATE OPERATIONS ====================

    def create(self, entity: ModelT) -> ModelT:
        """Create a new entity."""
        return self.repository.create(entity)

    def create_from_schema(self, schema: CreateSchemaT,
                          field_transformers: Dict[str, Callable[[Any], Any]] = None) -> ModelT:
        """Create a new entity from a Pydantic schema, applying optional field transformations."""
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
        """Update an existing entity."""
        entity.updated_at = int(time())
        return self.repository.update(entity)

    async def update_by_id(self, entity_id: str, schema: UpdateSchemaT,
                          field_handlers: Dict[str, Callable] = None) -> ModelT:
        """Update an entity by ID using data from a Pydantic schema, with optional custom field handlers."""
        existing = await self.get_by_id(entity_id)
        update_data = schema.model_dump(exclude_unset=True)

        # Applies custom handlers for specific fields
        if field_handlers:
            for field, value in update_data.items():
                if field in field_handlers:
                    field_handlers[field](existing, value)
                else:
                    setattr(existing, field, value)
        else:
            # Default behavior: set attributes directly
            for field, value in update_data.items():
                setattr(existing, field, value)

        existing.updated_at = int(time())
        return self.repository.update(existing)

    # ==================== DELETE OPERATIONS ====================

    async def delete(self, entity_id: str) -> None:
        """Delete an entity by ID, raising 404 if not found."""
        await self.get_by_id(entity_id)
        self.repository.delete(entity_id)

    # ==================== PAGINATION OPERATIONS ====================

    async def get_paginated(self, page: int, page_size: int) -> Dict[str, Any]:
        """Return paginated entities with metadata."""
        total = self.repository.count()
        total_pages = ceil(total / page_size) if total > 0 else 1
        offset = (page - 1) * page_size

        entities = self.repository.get_paginated(offset, page_size)

        return {
            "data": entities,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    async def get_paginated_by_store(self, store_id: str, page: int, page_size: int) -> Dict[str, Any]:
        """Return paginated entities for a specific store with metadata."""
        total = self.repository.count_by_store(store_id)
        total_pages = ceil(total / page_size) if total > 0 else 1
        offset = (page - 1) * page_size

        entities = self.repository.get_paginated_by_store(store_id, offset, page_size)

        return {
            "data": entities,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    async def get_all_by_store(self, store_id: str) -> Sequence[ModelT]:
        """Return all entities for a specific store."""
        return self.repository.get_all_by_store(store_id)
