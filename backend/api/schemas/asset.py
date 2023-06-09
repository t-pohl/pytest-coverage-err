from uuid import UUID

from pydantic import BaseModel

from .base_schemas import BaseSchema


class AssetCreate(BaseModel):
    name: str
    short_name: str
    type: str


class Asset(BaseSchema, AssetCreate):
    class Config:
        orm_mode = True


class AssetPairCreate(BaseModel):
    base_id: UUID
    quote_id: UUID


class AssetPair(BaseSchema, AssetPairCreate):
    base: Asset
    quote: Asset

    class Config:
        orm_mode = True
