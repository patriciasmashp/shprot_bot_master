from loguru import logger
from service.schemas.Style import Style
from service.DAO.BaseDAO import BaseDAO
from service.BaseApi.StrapiApi import StrapiApi


class StyleDAO(BaseDAO):
    schema = Style
    table = 'styleses'


    async def paginate(pageSize: int = 4, page: int = 1):
        url = f'/{StyleDAO.table}?pagination[pageSize]={pageSize}&pagination[page]={page}'
        logger.debug(url)
        
        res, pagination_data = await StrapiApi.get(url, pagination_data=True)
        if len(res) == 0:
            return []
        cities = []
        for city in res:
            cities.append(StyleDAO.schema(**city))
        
        return (cities, pagination_data)
