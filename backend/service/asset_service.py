from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas import (Asset, AssetCreate, AssetPair,
                                 AssetPairCreate, Page)
from backend.database.models import AssetModel, AssetPairModel
from backend.utils import database_utils


async def create_asset(asset: AssetCreate, db: AsyncSession) -> Asset:
    db_asset = AssetModel(
        name=asset.name,
        short_name=asset.short_name,
        type=asset.type,
    )
    database_utils.try_add(db, db_asset)
    await database_utils.try_commit(db)
    await database_utils.try_refresh(db, db_asset)
    return Asset.from_orm(db_asset)


async def retrieve_assets(
    page: int, size: int, short_name: Optional[str], db: AsyncSession
) -> Page[Asset]:  # pragma: no cover
    clauses = []
    if short_name:
        clauses.append(AssetModel.short_name == short_name)
    model_page = await database_utils.get_full_page(
        page, size, db, AssetModel, *clauses
    )
    return Page.from_orm_page(Asset, model_page)


async def retrieve_asset(asset_id: UUID, db: AsyncSession) -> Asset:
    db_asset = await db.get(AssetModel, asset_id)
    if db_asset is None:
        raise HTTPException(404, "Asset not found")
    return Asset.from_orm(db_asset)


async def delete_asset(asset_id: UUID, db: AsyncSession) -> None:
    db_asset = await db.get(AssetModel, asset_id)
    if db_asset is None:
        raise HTTPException(404, "Asset not found")
    await database_utils.try_delete_commit(db, db_asset)


async def create_asset_pair(asset_pair: AssetPairCreate, db: AsyncSession) -> AssetPair:
    db_asset_pair = AssetPairModel(
        base_id=asset_pair.base_id, quote_id=asset_pair.quote_id
    )
    await database_utils.try_add_commit_refresh(db, db_asset_pair)
    db_asset_pair_full = await database_utils.get_full(
        db_id=db_asset_pair.id, db=db, model_cls=AssetPairModel
    )
    return AssetPair.from_orm(db_asset_pair_full)


async def retrieve_asset_pairs(
    page: int,
    size: int,
    db: AsyncSession,
) -> Page[AssetPair]:  # pragma: no cover
    model_page = await database_utils.get_full_page(page, size, db, AssetPairModel)
    return Page.from_orm_page(AssetPair, model_page)


async def retrieve_asset_pair(asset_pair_id: UUID, db: AsyncSession) -> AssetPair:
    db_asset_pair = await database_utils.get_full(
        db_id=asset_pair_id, db=db, model_cls=AssetPairModel
    )
    if db_asset_pair is None:
        raise HTTPException(404, "Asset pair not found")
    return AssetPair.from_orm(db_asset_pair)


async def delete_asset_pair(asset_pair_id: UUID, db: AsyncSession) -> None:
    db_asset_pair = await db.get(AssetPairModel, asset_pair_id)
    if db_asset_pair is None:
        raise HTTPException(404, "Asset pair not found")
    await database_utils.try_delete_commit(db, db_asset_pair)
