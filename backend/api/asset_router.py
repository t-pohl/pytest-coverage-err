from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_204_NO_CONTENT

from backend.api.schemas import (Asset, AssetCreate, AssetPair,
                                 AssetPairCreate, Message, Page)
from backend.database import get_async_session
from backend.service import asset_service
from backend.settings import settings

router = APIRouter()


@router.post(
    "/",
    response_model=Asset,
    responses={409: {"model": Message}},
    description="""
    Creates a new asset. If a asset with the given short name already exists a 409 response is returned.""",
)
async def post_asset(
    asset: AssetCreate, db: AsyncSession = Depends(get_async_session)
) -> Asset:
    return await asset_service.create_asset(asset, db)


@router.get("/{assetId}", responses={404: {"model": Message}}, response_model=Asset)
async def get_asset(
    assetId: UUID, db: AsyncSession = Depends(get_async_session)
) -> Asset:
    return await asset_service.retrieve_asset(assetId, db)


@router.get("/", response_model=Page[Asset])
async def get_assets(
    page: int = 1,
    size: int = settings.default_page_size,
    short_name: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
) -> Page[Asset]:  # pragma: no cover
    return await asset_service.retrieve_assets(page, size, short_name, db)


@router.delete(
    "/{assetId}", responses={404: {"model": Message}}, status_code=HTTP_204_NO_CONTENT
)
async def delete_asset(
    assetId: UUID, db: AsyncSession = Depends(get_async_session)
) -> Response:  # pragma: no cover
    await asset_service.delete_asset(assetId, db)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post(
    "/pairs/",
    response_model=AssetPair,
    responses={409: {"model": Message}},
)
async def post_asset_pair(
    asset_pair: AssetPairCreate, db: AsyncSession = Depends(get_async_session)
) -> AssetPair:
    return await asset_service.create_asset_pair(asset_pair, db)


@router.get(
    "/pairs/{assetPairId}",
    responses={404: {"model": Message}},
    response_model=AssetPair,
)
async def get_asset_pair(
    assetPairId: UUID, db: AsyncSession = Depends(get_async_session)
) -> AssetPair:
    return await asset_service.retrieve_asset_pair(assetPairId, db)


@router.get("/pairs/", response_model=Page[AssetPair])
async def get_asset_pairs(
    page: int = 1,
    size: int = settings.default_page_size,
    db: AsyncSession = Depends(get_async_session),
) -> Page[AssetPair]:  # pragma: no cover
    return await asset_service.retrieve_asset_pairs(page, size, db)


@router.delete(
    "/pairs/{assetPairId}",
    responses={404: {"model": Message}},
    status_code=HTTP_204_NO_CONTENT,
)
async def delete_asset_pair(
    assetPairId: UUID, db: AsyncSession = Depends(get_async_session)
) -> Response:  # pragma: no cover
    await asset_service.delete_asset_pair(assetPairId, db)
    return Response(status_code=HTTP_204_NO_CONTENT)
