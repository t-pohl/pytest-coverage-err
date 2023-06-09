from fastapi import APIRouter

from .asset_router import router as asset_router

router = APIRouter()

router.include_router(asset_router, prefix="/assets", tags=["assets"])

