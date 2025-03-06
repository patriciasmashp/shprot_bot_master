from typing import List
from pydantic import BaseModel
from service.BaseApi.mixins.StrapiFormDataMixin import StrapiFormDataMixin
from service.BaseApi.BaseApi import BaseApi
from config import STRAPI_BASE_URL, STRAPI_TOKEN


class StrapiApi(BaseApi, StrapiFormDataMixin):

    async def get(url: str,
                  params: dict | str | None = None,
                  pagination_data: bool = False):
        url = f"{STRAPI_BASE_URL}" + url

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {STRAPI_TOKEN}"
        }

        result = await StrapiApi._get(url, headers=headers)
        if result:
            if pagination_data:
                return (result["data"], result["meta"]["pagination"])
            return result["data"]
        else:
            return None

    async def post(url: str, data: dict | BaseModel):
        if issubclass(data.__class__, BaseModel):
            data = data.model_dump(exclude_unset=True)
        data = {"data": data}
        url = f"{STRAPI_BASE_URL}" + url
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {STRAPI_TOKEN}"
        }

        result = await StrapiApi._post(url, data, headers=headers)
        if result:
            return result["data"]
        else:
            return None

    async def put(url: str, data: dict | BaseModel):
        if issubclass(data.__class__, BaseModel):
            data = data.model_dump(exclude_unset=True)
        data = {"data": data}
        url = f"{STRAPI_BASE_URL}" + url
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {STRAPI_TOKEN}"
        }
        result = await StrapiApi._put(url, data, headers=headers)
        if result:
            return result["data"]
        else:
            return None

    async def postFD(url: str,
                     data: List[dict] | List[BaseModel],
                     params: dict | str | None = None,
                     headers: dict = None):

        data_objs = []
        for value in data:

            if issubclass(value.__class__, BaseModel):
                value = value.model_dump(exclude_unset=True)
                data_objs.append(value)

        if len(data_objs) != 0:
            data = data_objs

        url = f"{STRAPI_BASE_URL}" + url

        headers = {"Authorization": f"Bearer {STRAPI_TOKEN}"}

        result = StrapiApi.upload_file(url, data, headers=headers)
        if result:
            return result
        else:
            return None

    async def delete(url: str):
        url = f"{STRAPI_BASE_URL}" + url
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {STRAPI_TOKEN}"
        }
        await StrapiApi._delete(url, headers=headers)
        
        return None
