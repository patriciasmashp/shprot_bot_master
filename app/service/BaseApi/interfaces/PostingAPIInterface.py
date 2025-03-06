from abc import ABC, abstractmethod
from typing import List


class PostingAPIInterface(ABC):

    @abstractmethod
    def post_photo(message: str, images: List[bytes]):
        pass

    @abstractmethod
    def post_video(video: bytes, message: str):
        pass
