from __future__ import annotations

from typing import Generic, Type, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

from backend.database import Base
from backend.utils import database_utils

Schema = TypeVar("Schema", bound=BaseModel)
Model = TypeVar("Model", bound=Base)


class Page(GenericModel, Generic[Schema]):
    items: list[Schema]
    total: int
    page: int
    size: int

    @staticmethod
    def from_orm_page(
        schema_cls: Type[Schema], models: database_utils.ModelPage[Model]
    ) -> Page[Schema]:
        items: list[Schema] = []
        for item in models.items:
            items.append(schema_cls.from_orm(item))
        return Page[Schema](
            items=items,
            total=models.total,
            page=models.page,
            size=models.size,
        )
