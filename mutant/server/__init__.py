from abc import ABC, abstractmethod

# from mutant.server.utils.error_reporting import init_error_reporting
from mutant.server.utils.telemetry.capture import Capture


class Server(ABC):

    def __init__(self, settings):
        pass
        # init_error_reporting()
