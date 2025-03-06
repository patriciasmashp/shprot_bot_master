import enum


class TatooType(enum.Enum):
    BLACK = "Ч/Б"
    COLORED = "Цвет"
    BOTH = "Оба варианта"


class PaginateAct(str, enum.Enum):
    next = "next_page"
    prev = "prev_page"
    set = "set"
    add = "add"
