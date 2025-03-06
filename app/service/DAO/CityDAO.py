from loguru import logger
from service.schemas.City import CityPydantic
from service.DAO.BaseDAO import BaseDAO
from service.BaseApi.StrapiApi import StrapiApi


class CityDAO(BaseDAO):
    schema = CityPydantic
    table = 'cities'

    async def get_all():
        url = f'/{CityDAO.table}?filters[enable][$eq]=true'
        res = await StrapiApi.get(url)

        if res is None:
            return []

        for item in res:
            item = CityDAO.schema(**item)

        return res

    async def paginate(pageSize: int = 4, page: int = 1):
        url = f'/{CityDAO.table}?pagination[pageSize]={pageSize}&pagination[page]={page}'

        res, pagination_data = await StrapiApi.get(url, pagination_data=True)
        if len(res) == 0:
            return []
        cities = []
        for city in res:
            cities.append(CityDAO.schema(**city))
        
        return (cities, pagination_data)
