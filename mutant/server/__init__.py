from abc import ABC, abstractmethod

# from mutant.server.utils.error_reporting import init_error_reporting
from mutant.server.utils.telemetry.capture import Capture


class Server(ABC):

    def __init__(self, settings):
        self._mutant_telemetry = Capture()
        self._mutant_telemetry.capture("server-start")
        # init_error_reporting()
