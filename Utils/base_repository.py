from typing import TypeVar, Generic, Sequence, Type
from sqlmodel import Session, select

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Repositório genérico que implementa operações CRUD padrão para qualquer modelo.
    Reduz duplicação de código entre repositories específicos.
    """

    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def create(self, entity: T) -> T:
        """Cria uma nova entidade no banco de dados."""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update(self, entity: T) -> T:
        """Atualiza uma entidade existente no banco de dados."""
        existing = self.get_by_id(entity.id)
        if not existing:
            raise ValueError(f"{self.model.__name__} with id {entity.id} not found")
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get_all(self) -> Sequence[T]:
        """Retorna todas as entidades do tipo."""
        return self.session.exec(select(self.model)).all()

    def get_by_id(self, entity_id: str) -> T | None:
        """Retorna uma entidade pelo ID."""
        return self.session.get(self.model, entity_id)

    def delete(self, entity_id: str) -> None:
        """Deleta uma entidade pelo ID."""
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
        else:
            raise ValueError(f"{self.model.__name__} with id {entity_id} not found")
