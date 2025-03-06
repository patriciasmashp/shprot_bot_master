from urllib.parse import urlencode
import uuid
import aiohttp
from loguru import logger
from pydantic import BaseModel
import requests

from service.BaseApi.interfaces.FormDataMixin import AbstractFormDataMixin


class StrapiFormDataMixin(AbstractFormDataMixin):

    def upload_file(url: str,
                    data: dict | BaseModel,
                    params: dict | str | None = None,
                    headers: dict = None):
        if type(params) is dict:
            params = urlencode(params)
        if issubclass(data.__class__, BaseModel):
            data = data.model_dump()
        if params:
            url = url + "?" + params

        files = []
        for file in data["files"]:
            files.append(('files', (str(uuid.uuid4()), file, 'image/*')))

        response = requests.request("POST",
                                    url,
                                    headers=headers,
                                    data=data,
                                    files=files)

        return response

    async def _postFD(url: str,
                      data: dict | BaseModel,
                      params: dict | str | None = None,
                      headers: dict = None):
        """aiohttp отпарвляет в part дополнительный заголовок из-за чего strapi не прикрепляет файлы к записи"""

        if type(params) is dict:
            params = urlencode(params)
        if issubclass(data.__class__, BaseModel):
            data = data.model_dump()
        if params:
            url = url + "?" + params
        fd = aiohttp.FormData()
        async with aiohttp.ClientSession() as session:

            #     with aiohttp.MultipartWriter("form-data") as mp:
            try:
                for key, value in data.items():
                    # logger.debug(value)
                    if isinstance(value, bytes):

                        logger.debug(key)
                        fd.add_field(key,
                                     value,
                                     filename=str(uuid.uuid4()),
                                     content_type="image/*")
                    else:
                        fd.add_field(key, value)

                    # part = mp.append(value)
                    # part.set_content_disposition('form-data', name=key)
            except Exception as e:
                logger.error(e)
            
            
            resp = await session.post(
                url,
                headers=headers,
                data=fd,
            )
            res = await resp.json()
            logger.debug(res)
            
            return res
