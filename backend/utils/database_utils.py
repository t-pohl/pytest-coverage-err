import enum
import sys
from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import RelationshipProperty, selectinload
from sqlalchemy.sql.elements import BinaryExpression

import backend.database.models  # noqa : needs to be imported to relationship reflection
from backend.api.schemas import BaseSchema
from backend.database import Base

from .cache import Cache
from .enums import SortDir
from .exceptions import PaginationException

T = TypeVar("T")
FullSchema = TypeVar("FullSchema", bound=BaseSchema)
Schema = TypeVar("Schema", bound=BaseModel)
Model = TypeVar("Model", bound=Base)
Model_ = TypeVar("Model_", bound=Base)
EnumType = TypeVar("EnumType", bound=enum.Enum)

IntegrityDelegate = Callable[[IntegrityError], None]


@dataclass
class IntegrityHandler:
    restrict: int | IntegrityDelegate = 400
    not_null: int | IntegrityDelegate = 400
    foreign_key: int | IntegrityDelegate = 400
    unique: int | IntegrityDelegate = 409
    check: int | IntegrityDelegate = 400
    exclusion: int | IntegrityDelegate = 400
    default: int | IntegrityDelegate = 500

    def handle(self, e: IntegrityError) -> None:
        match e.orig.sqlstate:
            case "23001":  # RestrictViolationError
                IntegrityHandler.handle_case(e, self.restrict)
            case "23002":  # NotNullViolationError
                IntegrityHandler.handle_case(e, self.not_null)
            case "23503":  # ForeignKeyViolationError
                IntegrityHandler.handle_case(e, self.foreign_key)
            case "23505":  # UniqueViolationError
                IntegrityHandler.handle_case(e, self.unique)
            case "23514":  # CheckViolationError
                IntegrityHandler.handle_case(e, self.check)
            case "23P01":  # ExclusionViolationError
                IntegrityHandler.handle_case(e, self.exclusion)
            case _:
                IntegrityHandler.handle_case(e, self.default)

    @staticmethod
    def handle_case(e: IntegrityError, handler: int | IntegrityDelegate) -> None:
        if isinstance(handler, int):
            raise HTTPException(status_code=handler, detail=e.args[0])
        handler(e)


default_integrity_handler = IntegrityHandler()
default_delete_integrity_handler = IntegrityHandler(
    restrict=500, not_null=500, foreign_key=500, unique=500, check=500, exclusion=500
)


def get_first(
    entities: list[FullSchema], function: Callable[[FullSchema], bool], msg: str
) -> FullSchema:
    result = next(filter(function, entities), None)
    if result is None:  # pragma: no cover
        raise HTTPException(status_code=404, detail=msg)
    return result


def get_first_by(
    entities: list[FullSchema], key: str, value: T, msg: str
) -> FullSchema:
    return get_first(entities, lambda o: getattr(o, key) == value, msg)  # type: ignore[no-any-return]


def newest(entities: list[FullSchema], n: int = 1) -> list[FullSchema]:
    return sorted(entities, key=lambda v: v.updated_at, reverse=True)[0:n]


async def try_commit(
    db: AsyncSession, handler: IntegrityHandler = default_integrity_handler
) -> None:
    try:
        await db.commit()
    except IntegrityError as e:
        handler.handle(e)


def try_add(
    db: AsyncSession, entity: Any, handler: IntegrityHandler = default_integrity_handler
) -> None:
    try:
        db.add(entity)
    except IntegrityError as e:  # pragma: no cover
        handler.handle(e)


async def try_refresh(
    db: AsyncSession, entity: Any, handler: IntegrityHandler = default_integrity_handler
) -> None:
    try:
        await db.refresh(entity)
    except IntegrityError as e:  # pragma: no cover
        handler.handle(e)


async def try_delete(
    db: AsyncSession,
    entity: Any,
    handler: IntegrityHandler = default_delete_integrity_handler,
) -> None:
    try:
        await db.delete(entity)
    except IntegrityError as e:
        handler.handle(e)


async def try_add_commit_refresh(
    db: AsyncSession, entity: Any, handler: IntegrityHandler = default_integrity_handler
) -> None:
    try_add(db=db, entity=entity, handler=handler)
    await try_commit(db=db, handler=handler)
    await try_refresh(db=db, entity=entity, handler=handler)


async def try_delete_commit(
    db: AsyncSession,
    entity: Any,
    handler: IntegrityHandler = default_delete_integrity_handler,
) -> None:
    await try_delete(db, entity, handler)
    await try_commit(db)


def _get_relationships(model_cls: Type[Model]) -> dict[str, Type[Model_]]:
    return {
        key: getattr(sys.modules["backend.database.models"], value.argument)
        for (key, value) in model_cls.__mapper__._init_properties.items()
        if isinstance(value, RelationshipProperty)
    }


_relationships = Cache(_get_relationships)


def _get_select_in_loads(
    model_cls: Type[Model], base: Optional[Any] = None
) -> list[Any]:
    result: list[Any] = []
    for key, sub_cls in _relationships[model_cls].items():
        prop = getattr(model_cls, key)
        sil = selectinload(prop) if base is None else base.selectinload(prop)
        result += _get_select_in_loads(sub_cls, sil)
    return result if base is None or result != [] else [base]


_selectinloads = Cache(_get_select_in_loads)


async def get_full(
    db_id: UUID, db: AsyncSession, model_cls: Type[Model]
) -> Optional[Model]:
    stmt = (
        select(model_cls)
        .where(model_cls.id == db_id)
        .limit(1)
        .options(*_selectinloads[model_cls])
    )
    result = await db.execute(stmt)
    return result.scalars().first()  # type: ignore[no-any-return]


@dataclass
class ModelPage(Generic[Model]):
    items: list[Model]
    total: int
    page: int
    size: int


async def get_full_page(
    page: int,
    size: int,
    db: AsyncSession,
    model_cls: Type[Model],
    *where_clauses: list[BinaryExpression],
    joins: Optional[
        list[Union[Type[Model_], tuple[Type[Model_], BinaryExpression]]]
    ] = None,
    order_by: Optional[EnumType] = None,
    order_dir: SortDir = SortDir.asc,
) -> ModelPage[Model]:
    if page < 1:
        raise PaginationException("Page number smaller than one not possible.")
    if size < 1:
        raise PaginationException("Page size smaller than one not possible.")

    count_stmt = select([func.count()]).select_from(model_cls.__table__)
    page_stmt = select(model_cls)

    if joins is not None:
        for join_clause in joins:
            if isinstance(join_clause, tuple):
                count_stmt = count_stmt.join(*join_clause)
                page_stmt = page_stmt.join(*join_clause)
            else:
                count_stmt = count_stmt.join(join_clause)
                page_stmt = page_stmt.join(join_clause)

    if order_by is not None:
        if order_by.value not in model_cls.__dict__:
            raise HTTPException(
                status_code=500, detail="Sorting column not found on model."
            )
        column = model_cls.__dict__[order_by.value]
        page_stmt = page_stmt.order_by(
            column.asc() if order_dir == SortDir.asc else column.desc()
        )

    for clause in where_clauses:
        page_stmt = page_stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    page_stmt = (
        page_stmt.offset((page - 1) * size)
        .limit(size)
        .options(*_selectinloads[model_cls])
    )

    count_result = await db.execute(count_stmt)
    page_result = await db.execute(page_stmt)

    return ModelPage(
        total=count_result.scalar(),
        page=page,
        size=size,
        items=page_result.scalars().all(),
    )
