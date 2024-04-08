from abc import ABC, abstractmethod

# from mutantdb.server.utils.error_reporting import init_error_reporting
from mutantdb.server.utils.telemetry.capture import Capture


class Server(ABC):

    def __init__(self, settings):
        pass
        # init_error_reporting()
