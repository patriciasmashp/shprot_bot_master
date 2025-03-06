import asyncio
from datetime import datetime, timedelta
import json
from loguru import logger
import requests
from service.BaseApi.StrapiApi import StrapiApi
from service.BaseApi.BaseApi import BaseApi
from service.BaseApi.interfaces.PostingAPIInterface import PostingAPIInterface
from config import IG_ID


class InstagramAPI(BaseApi, PostingAPIInterface):

    async def __get_token():

        token_data = await StrapiApi.get("/instagram-token")

        dt = datetime.strptime(token_data["expire"], "%Y-%m-%dT%H:%M:%S.%fZ")
        token_expired = dt - timedelta(days=30) < datetime.now()

        if token_expired:
            res = await BaseApi._get(
                f"https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token={token_data['token']}"
            )
            expire = datetime.now() + timedelta(seconds=res["expires_in"])

            await StrapiApi.put(
                "/instagram-token", {
                    "expire": expire.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "token": res["access_token"]
                })
            return {
                "token": res["access_token"],
                "expire": expire.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }

        return {"token": token_data["token"], "expire": token_data["expire"]}

    @classmethod
    async def post_photo(cls, images, message):
        token_data = await cls.__get_token()
        is_corusel = len(images) > 1
        headers = {"Authorization": f"Bearer {token_data['token']}"}
        container_ids = []

        for image in images:
            create_container_url = f"https://graph.instagram.com/v22.0/{IG_ID}/media?is_carousel_item={'true' if is_corusel else 'false'}&image_url={image}"
            container_res = await BaseApi._post(create_container_url,
                                                data={"caption": message},
                                                headers=headers)
            container_ids.append(container_res["id"])

        logger.debug(container_ids)
        if is_corusel:
            carusel_url = f"https://graph.instagram.com/v22.0/{IG_ID}/media"
            carusel_data = {
                "media_type": "CAROUSEL",
                "children": ",".join(container_ids),
                "caption": message
            }

            container_res = await BaseApi._post(carusel_url,
                                                data=carusel_data,
                                                headers=headers)
        publish_url = f"https://graph.instagram.com/v22.0/{IG_ID}/media_publish"
        publis_res = await BaseApi._post(
            publish_url,
            data={"creation_id": container_res["id"]},
            headers=headers)
        logger.debug(publis_res)

    @classmethod
    async def post_video(cls, video, message):
        token_data = await cls.__get_token()
        headers = {"Authorization": f"Bearer {token_data['token']}"}

        create_container_url = f"https://graph.instagram.com/v22.0/{IG_ID}/media?is_carousel_item=true&video_url={video}&media_type=VIDEO"
        container_res = await BaseApi._post(create_container_url,
                                            params={},
                                            data={},
                                            headers=headers)
        await asyncio.sleep(5)
        logger.debug(video)
        
        
        publish_url = f"https://graph.instagram.com/v22.0/{IG_ID}/media_publish"
        publis_res = await BaseApi._post(
            publish_url,
            data={"creation_id": container_res["id"]},
            headers=headers)
        logger.debug(publis_res)
