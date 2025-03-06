from typing import List

from pydantic import Field, computed_field
from service.schemas.City import CityPydantic
from service.schemas.Style import Style
from service.schemas.StrapiBase import StrapiBase


class Master(StrapiBase):
    name: str
    master_id: int
    username: str = Field(default="")
    master_url: str
    about_master: str
    validated: bool | None = Field(default=None)
    name: str
    city: str | CityPydantic | None = Field(default=None)
    phone_number: str
    profile_image: str | bytes | dict | None = Field(default=None)
    is_notifications_allowed: bool = Field(default=True)
    is_blocked: bool = Field(default=False)
    photos: List[dict | bytes] | bytes | None = Field(default=None)
    styles: List[Style | str] | None = Field(default=None)
    balance: int | None = Field(default=0)
    likes: int = Field(default=0)

    @computed_field
    @property
    def styles_names(self) -> List[str]:
        if self.styles is None:
            return []
        if len(self.styles) != 0:
            styles = []
            if isinstance(self.styles[0], Style):
                for style in self.styles:
                    styles.append(style.style_name)

                return styles
        return self.styles

    def to_upload(self) -> dict:
        excluded_fileds = set(StrapiBase.model_fields.keys())
        excluded_fileds.update({'styles_names'})
        master = self.model_dump(exclude=excluded_fileds)
        master["city"] = self.city.documentId

        photos = []
        if self.photos is not None:
            for photo in self.photos:
                photos.append(photo["id"])
            master["photos"] = photos

        master["profile_image"] = self.profile_image["id"]

        if self.styles is not None:
            styles = []
            if isinstance(self.styles[0], Style):
                for style in self.styles:
                    styles.append(style.documentId)
                master["styles"] = styles

        return master
