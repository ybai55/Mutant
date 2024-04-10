from abc import ABC, abstractmethod

from mutantdb.config import Settings


class Server(ABC):
    @abstractmethod
    def __init__(self, settings: Settings):
        pass
