from abc import ABC, abstractmethod

from pydantic import BaseModel


class AbstractFormDataMixin(ABC):

    @abstractmethod
    def upload_file(url: str,
                    data: dict | BaseModel,
                    params: dict | str | None = None,
                    headers: dict = None) -> dict:
        pass
