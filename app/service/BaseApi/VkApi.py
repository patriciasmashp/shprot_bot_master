from datetime import datetime, timedelta
import io
from typing import List
from loguru import logger
import requests
import vk_api
from service.BaseApi.interfaces.PostingAPIInterface import PostingAPIInterface
from .BaseApi import BaseApi
from config import VK_GROUP_ID, VK_USER_TOKEN, VK_APP_ID


class VkApi(BaseApi, PostingAPIInterface):
    scopes = 'wall, photos, video, group'
    user_session = vk_api.VkApi(app_id=VK_APP_ID,
                                login="89193898194",
                                password="v6=.P.Qm",
                                token=VK_USER_TOKEN,
                                scope=scopes)
    user_api = user_session.get_api()

    @classmethod
    async def post_photo(cls,
                         message: str,
                         images: List[bytes] = None,
                         from_group=VK_GROUP_ID):

        # await cls.upload_photos(images)
        upload = vk_api.VkUpload(cls.user_session)
        file_images = []
        for image in images:
            file_images.append(io.BytesIO(image))

        photo_list = upload.photo_wall(file_images)

        attachment = ','.join('photo{owner_id}_{id}'.format(**item)
                              for item in photo_list)
        publish_date = datetime.now() + timedelta(days=7)
        logger.debug(publish_date.timestamp())
        logger.debug(type(publish_date))
        
        cls.user_api.wall.post(owner_id=from_group,
                               message=message,
                               from_group=True,
                               publish_date=publish_date.timestamp(),
                               attachments=attachment)

    @classmethod
    async def post_video(cls,
                         video: bytes,
                         from_group=VK_GROUP_ID,
                         message: str = ""):

        params = {
            'access_token': VK_USER_TOKEN,
            'name': "videio.mp4",
            'group_id': from_group * -1,
            'v': 5.199
        }
        get_video_upload_url = requests.get(
            'https://api.vk.com/method/video.save', params=params)

        video_upload_url = get_video_upload_url.json(
        )["response"]["upload_url"]
        resp = requests.post(video_upload_url,
                             params=params,
                             files={'video_file': io.BytesIO(video)})

        attachment = 'video{owner_id}_{video_id}'.format(**resp.json())

        cls.user_api.wall.post(owner_id=from_group,
                               message=message,
                               attachments=attachment)
