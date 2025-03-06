from typing import List

from loguru import logger

from service.DAO.AdminDAO import AdminDAO
from service.schemas.City import CityPydantic
from service.schemas.Style import Style
from service.schemas.StrapiBase import StrapiBase
from service.schemas.Master import Master
from service.BaseApi.StrapiApi import StrapiApi


class MasterDAO:

    async def get_masters():
        "Получить список всех мастеров со связанными полями"
        url = "/masters?populate=*"
        masters = await StrapiApi.get(url)
        result = []

        for master in masters:
            master = Master(**master)
            result.append(master)

        return result

    async def create_master(master: Master):
        "Создать мастера"

        url = "/masters"
        photos = master.photos
        profile_image = master.profile_image

        excluded_fileds = set(StrapiBase.model_fields.keys())
        excluded_fileds.update({'photos', 'profile_image', 'styles_names'})

        create_response = await StrapiApi.post(
            url, master.model_dump(exclude=excluded_fileds))

        master = Master(**create_response)

        upload_url = "/upload/"

        await StrapiApi.postFD(
            upload_url, {
                "ref": "api::master.master",
                "refId": master.id,
                "field": "profile_image",
                "files": [profile_image],
            })

        await StrapiApi.postFD(
            upload_url, {
                "ref": "api::master.master",
                "refId": master.id,
                "field": "photos",
                "files": photos,
            })

        return master

    async def get_master_by_tg_id(tg_id: str | int, populate=True):
        if populate:
            url = f"/masters?filters[master_id][$eq]={tg_id}&populate=*"
        else:
            url = f"/masters?filters[master_id][$eq]={tg_id}"
        master = await StrapiApi.get(url)
        if len(master) == 0:
            return None

        return Master(**master[0])

    async def get_master(document_id: str):

        url = f"/masters/{document_id}?populate=*"

        master = await StrapiApi.get(url)

        if master is None:
            return None

        return Master(**master)

    async def update_master(master: Master | dict, document_id: str):

        url = f"/masters/{document_id}"

        if isinstance(master, Master):
            excluded_fileds = set(StrapiBase.model_fields.keys())
            excluded_fileds.update({'photos', 'profile_image', 'styles_names'})
            if master.styles:
                if isinstance(master.styles[0], Style):
                    styles = []
                    for style in master.styles:
                        styles.append(style.documentId)
                    master.styles = styles

            if isinstance(master.city, CityPydantic):
                master.city = master.city.documentId

            await StrapiApi.put(url,
                                master.model_dump(exclude=excluded_fileds))

        else:

            await StrapiApi.put(url, master)

    async def update_photos(tg_id: int, photos: List[bytes]):
        master: Master = await MasterDAO.get_master_by_tg_id(tg_id)

        for photo in master.photos:
            url = f"/upload/files/{photo['id']}"
            await StrapiApi.delete(url)

        upload_url = "/upload/"
        await StrapiApi.postFD(
            upload_url, {
                "ref": "api::master.master",
                "refId": master.id,
                "field": "photos",
                "files": photos,
            })

    async def delete_master(document_id: str):

        url = f"/masters/{document_id}"
        await StrapiApi.delete(url)

    async def update_city(document_id: str, city: str):

        url = f"/masters/{document_id}"
        await StrapiApi.put(url, {"city": city})

    async def update_styles(document_id: str, styles: List[str]):

        url = f"/masters/{document_id}"
        await StrapiApi.put(url, {"styles": styles})

    async def update_main_photo(document_id: str, main_photo: bytes):

        master: Master = await MasterDAO.get_master(document_id)
        old_photo = master.profile_image
        url = f"/upload/files/{old_photo['id']}"
        await StrapiApi.delete(url)

        upload_url = "/upload/"
        await StrapiApi.postFD(
            upload_url, {
                "ref": "api::master.master",
                "refId": master.id,
                "field": "profile_image",
                "files": [main_photo],
            })

    async def aqure_bonuses(document_id: str):
        bonuses_from_post = await AdminDAO.get_bot_settings(
            setting="bonuses_from_post")

        url = f"/masters/{document_id}"
        master = await StrapiApi.get(url)

        await StrapiApi.put(url,
                            {"balance": master["balance"] + bonuses_from_post})
