
from datetime import datetime
from pydantic import BaseModel, Field


class StrapiBase(BaseModel):
    id: int | None = Field(default=None)
    documentId: str | None = Field(default=None)
    createdAt: datetime | None = Field(default=None)
    updatedAt: datetime | None = Field(default=None)
    publishedAt: datetime | None = Field(default=None)
    locale: str = Field(default="ru-RU")