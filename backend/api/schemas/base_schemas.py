from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseSchemaWOId(BaseModel):
    created_at: datetime
    updated_at: datetime


class BaseSchema(BaseSchemaWOId):
    id: UUID
