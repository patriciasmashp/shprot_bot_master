from typing import List, Type
from loguru import logger
from pydantic import BaseModel

from service.BaseApi.StrapiApi import StrapiApi


class BaseDAO:

    table: str = None
    schema: BaseModel = None

    @classmethod
    async def get_by_document_id(cls, document_id) -> Type[schema]:
        url = f'/{cls.table}/{document_id}'
        res = await StrapiApi.get(url)
        
        if res is None:
            return None
        
        return cls.schema(**res)
        
    
    @classmethod
    async def get_all(cls):
        url = f'/{cls.table}'

        res = await StrapiApi.get(url)
        if res is None:
            return []

        models = []
        for item in res:
            models.append(cls.schema(**item))

        return models

    @classmethod
    async def paginate(cls, pageSize: int = 4, page: int = 1):
        url = f'/{cls.table}?pagination[pageSize]={pageSize}&pagination[page]={page}'

        res = await StrapiApi.get(url)
        if res is None:
            return None

        return cls.schema(**res)
