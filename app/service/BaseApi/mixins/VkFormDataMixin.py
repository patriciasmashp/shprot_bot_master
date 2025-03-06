from urllib.parse import urlencode
import uuid
import aiohttp
from loguru import logger
from pydantic import BaseModel
import requests

from service.BaseApi.interfaces.FormDataMixin import AbstractFormDataMixin


class VkFormDataMixin(AbstractFormDataMixin):

    def upload_file(url: str,
                    data: dict | BaseModel,
                    params: dict | str | None = None,
                    headers: dict = None):
        
        url = "https://pu.vk.com/c517536/ss2242/upload.php?act=do_add&mid=171791677&aid=299090198&gid=223349418&hash=c19ac1f700c713ead8f9d6987a295807&rhash=1947e47adf80ce46c8c094de222d0150&swfupload=1&api=1"

        payload = {}
        logger.debug(data["files"][0])
        with open("./test.png", 'wb') as f:
            f.write(data["files"][0])
        files = [('photo', ('1ef8a7e6-b8b5-4320-972e-a641e167b4a4',
                            open("./test.png",
                                 'rb'), 'application/octet-stream'))]
        headers = {
            'Cookie':
            'remixff=0; remixlang=0; remixlgck=e6e009b2eaf553711b; remixstid=546766370_BGesJwLz67P1X1SSARfPHTnvN1RGSyvrWltKu3N6Wls; remixstlid=9120408720954179262_OJ8oaFo8ivhaZNegC4zEVXbNxmIEFpoOAS84KGSYKvD; remixua=-1%7C-1%7C53%7C1803870298'
        }
        proxies = {
            "http": "http://127.0.0.1:8181",
            # "https": "https://127.0.0.1:8181",
        }
        response = requests.post(url,
                                 files=files)

        # print(response.text)
        return response.text
        if type(params) is dict:
            params = urlencode(params)
        if issubclass(data.__class__, BaseModel):
            data = data.model_dump()
        if params:
            url = url + "?" + params

        files = []
        for index, file in enumerate(data["files"]):
            files.append(('photo', (str(uuid.uuid4()), file,
                                    'application/octet-stream')))

        logger.debug(files)
        files = [('photo', ('1ef8a7e6-b8b5-4320-972e-a641e167b4a4',
                            data["files"][0], 'application/octet-stream'))]
        response = requests.request(
            "POST",
            url,
            headers=headers,
            # data=data,
            files=files)

        return response.json()

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
