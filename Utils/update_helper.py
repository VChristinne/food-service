from typing import Any, Callable, Dict, TypeVar
from time import time

T = TypeVar("T")


class UpdateHelper:
    """
    Helper para aplicar atualizações genéricas em entidades.
    Reduz duplicação de lógica match/case em services.
    """

    @staticmethod
    def apply_updates(
        entity: T,
        update_data: Dict[str, Any],
        field_handlers: Dict[str, Callable[[T, Any], None]] = None,
    ) -> T:
        """
        Aplica atualizações em uma entidade usando handlers personalizados por campo.

        Args:
            entity: Entidade a atualizar
            update_data: Dados do update (obtido de schema.model_dump(exclude_unset=True))
            field_handlers: Dict {nome_campo: função_handler(entity, value)}

        Returns:
            A entidade atualizada
        """
        if field_handlers is None:
            field_handlers = {}

        for field, value in update_data.items():
            if field in field_handlers:
                # Usa handler customizado
                field_handlers[field](entity, value)
            else:
                # Usa setattr padrão
                setattr(entity, field, value)

        # Atualiza timestamp
        entity.updated_at = int(time())
        return entity

    @staticmethod
    def build_simple_handlers(field_mappings: Dict[str, str] = None) -> Dict[str, Callable]:
        """
        Cria handlers simples para mapeamento de campos 1:1.

        Args:
            field_mappings: Dict {campo_entrada: campo_saida}

        Returns:
            Dict de handlers
        """
        if field_mappings is None:
            field_mappings = {}

        handlers = {}
        for input_field, output_field in field_mappings.items():
            handlers[input_field] = lambda e, v, of=output_field: setattr(e, of, v)

        return handlers
