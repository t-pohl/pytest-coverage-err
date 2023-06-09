from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base
from backend.database.models.database_mixins import StandardMixin


class AssetModel(Base, StandardMixin):  # type: ignore
    __tablename__ = "assets"
    name = Column(String, nullable=False)
    short_name = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)


class AssetPairModel(Base, StandardMixin):  # type: ignore
    __tablename__ = "asset_pairs"
    base_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    base = relationship("AssetModel", uselist=False, foreign_keys=[base_id])
    quote_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    quote = relationship("AssetModel", uselist=False, foreign_keys=[quote_id])
