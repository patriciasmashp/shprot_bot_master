
from datetime import datetime

from pydantic import Field
from service.schemas.StrapiBase import StrapiBase


class CityPydantic(StrapiBase):
    name: str
    enable: bool
    createdAt: datetime | None = Field(default=datetime.now(), exclude=True)
    updatedAt: datetime | None = Field(default=datetime.now(), exclude=True)
    publishedAt: datetime | None = Field(default=datetime.now(), exclude=True)