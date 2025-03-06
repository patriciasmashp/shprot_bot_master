import datetime
from dotenv import load_dotenv
from os import environ, path
from loguru import logger

load_dotenv()

TOKEN = environ["TOKEN"]
DEBUG = int(environ["DEBUG"])
STRAPI_BASE_URL = environ["STRAPI_BASE_URL"]
STRAPI_MEDIA_URL = environ["STRAPI_MEDIA_URL"]
STRAPI_TOKEN = environ["STRAPI_TOKEN"]

VK_USER_TOKEN = environ["VK_USER_TOKEN"]
VK_TOKEN = environ["VK_TOKEN"]
VK_GROUP_ID = int(environ["GROUP_ID"])
VK_APP_ID = int(environ["VK_APP_ID"])

S3_URL = environ["S3_URL"]
ACCESS_KEY = environ["ACCESS_KEY"]
SECRET_KEY = environ["SECRET_KEY"]
BUCKET_NAME = environ["BUCKET_NAME"]


PAGES_SIZE = 5

BASE_PATH = path.dirname(path.realpath(__file__))
ASSETS_PATH = path.join(BASE_PATH, 'images')

IG_ID = environ["IG_ID"]





# RABBIT_MQ_URL = environ["RABBIT_MQ_URL"]
# REDIS_HOST = environ["REDIS_HOST"]
# REDIS_PORT = environ["REDIS_PORT"]

