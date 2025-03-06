from typing import List
from service.BaseApi.StrapiApi import StrapiApi

welcome_msg = "Добро пожаловать"
pls_send_phone = "Отправьте номер телефона"


async def get_text_from_strapi(key: str):
    url = "/bot-text"
    texts = await StrapiApi.get(url)

    return texts["texts"][key]


async def anket_text(city: str, name: str, phone: str, styles: List[str],
                     about: str):
    text = await get_text_from_strapi("registration_show_anket")

    text += anket(city, name, phone, styles, about)

    return text


def anket(city: str, name: str, phone: str, styles: List[str], about: str):
    text = f"""\nИмя: {name}
Город: {city}

Телефон: {phone}

Стили: {', '.join(styles)}

О себе: {about}"""
    return text


async def anket_to_admin(name: str, username: str, city: str, phone: str,
                         styles: List[str], about: str, master_url: str):
    admin_text = await get_text_from_strapi("registration_admin_text")
    admin_text += f"""
Имя: {name}
Имя пользователя: {username}
Город: {city}

Телефон: {phone}

Стили: {', '.join(styles)}

О себе: {about}

Ссылка на мастера: {master_url}"""

    return admin_text


async def post_sketch(city: str, master_name: str, master_url, body_part: str,
                      price: int):
    text = await get_text_from_strapi("post_call_to_app")
    return f"""Город: {city}
Мастер: {master_name} {master_url}  
Место: {body_part}
Цена: {price}

{text}
"""


async def post_photo(city: str, style: str, time: str, master_name: str,
                     master_url, price: int):
    text = await get_text_from_strapi("post_call_to_app")
    return f"""Город: {city}
Стиль: {style}
Время работы: {time}
Мастер: {master_name} {master_url}  
Цена: {price}

{text}
"""


async def post_video(city: str, time: str, master_name: str, master_url,
                     price: int):
    text = await get_text_from_strapi("post_call_to_app")
    return f"""Город: {city}
Время работы: {time}
Мастер: {master_name} {master_url}  
Цена: {price}

{text}
"""
