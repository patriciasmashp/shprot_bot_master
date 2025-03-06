from typing import Optional
from aiogram.filters.callback_data import CallbackData

from service.enums import PaginateAct


class PaginateCallback(CallbackData, prefix="paginate"):
    act: PaginateAct
    set_id: Optional[int | str] = None
    current: Optional[int] = None
    max_page: Optional[int] = None
    offset: Optional[int] = None
    # limit: int = None
