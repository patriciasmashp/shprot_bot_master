from datetime import datetime
from typing import Dict, List

from pydantic import Field
from service.schemas.StrapiBase import StrapiBase

class Style(StrapiBase):
    style_name: str
    createdAt: datetime | None = Field(default=datetime.now(), exclude=True)
    updatedAt: datetime | None = Field(default=datetime.now(), exclude=True)
    publishedAt: datetime | None = Field(default=datetime.now(), exclude=True)