import logging
from typing import Callable, TypeAlias

from tcp_tui.messaging import RawNetworkMessage
from tcp_tui.services.queue import ThreadQueueProcessor

HandlerType: TypeAlias = Callable[[dict[str, str]], None]


class MessageHandler:
    def __init__(self, frequency: float = 0.1):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._handlers: dict[str, HandlerType] = {}
        self._queue = ThreadQueueProcessor[RawNetworkMessage](
            self._process, name="MessageHandlersQueue", frequency=frequency
        )

    def register(self, handle: str, func: HandlerType) -> None:
        self._handlers[handle] = func

    def put(self, message: RawNetworkMessage) -> None:
        self._queue.put(message)

    def start(self) -> None:
        self._queue.start()

    def stop(self) -> None:
        self._queue.stop()

    def _process(self, item: RawNetworkMessage) -> None:
        if item.handle not in self._handlers:
            self.logger.warning(f"No handler for message: {item}")
            return
        self._handlers[item.handle](item.data)
