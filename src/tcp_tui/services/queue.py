import threading
import logging
import queue
from typing import Callable
from time import sleep


class ThreadQueueProcessor[T]:
    def __init__(
        self,
        process: Callable[[T], None],
        name: str | None = None,
        frequency: float = 0.1,
    ):
        if name is None:
            self.name = f"{self.__class__.__name__}({process.__name__})"
        else:
            self.name = name

        self.logger = logging.getLogger(f"{self.__class__.__name__}[{self.name}]")
        self.process = process
        self.frequency = frequency
        self.thread: threading.Thread | None = None
        self._is_shutting_down = threading.Event()
        self.queue: queue.Queue[T] = queue.Queue[T]()

    @property
    def is_running(self) -> bool:
        return self.thread is not None and self.thread.is_alive()

    def start(self):
        self.logger.info("Starting thread")
        self._init_thread()

        if self.is_running:
            self.logger.warning("Thread is already running")
            return

        if self.thread is None:
            self.logger.error("Thread not initialized")
            return
        self.thread.start()

    def stop(self):
        self.logger.info("Stopping thread")

        if not self.is_running:
            self.logger.warning("Thread is not running")
            return

        if self.thread is None:
            self.logger.error("Thread not initialized")
            return

        self._is_shutting_down.set()
        self.clear_queue()
        try:
            self.thread.join()
        except Exception as e:
            self.logger.warning(f"Exception whilst joining thread: {e!r}")

    def put(self, item: T):
        self.queue.put(item, block=False)

    def clear_queue(self):
        with self.queue.mutex:
            self.queue.queue.clear()

    def _init_thread(self):
        if self.thread is not None:
            self.logger.error("Thread already initialized")
            return
        self.thread = threading.Thread(
            target=self._process, name=self.name, daemon=True
        )

    def _process(self):
        while not self._is_shutting_down.is_set():
            try:
                item: T = self.queue.get(block=False)
                self.process(item)
            except queue.Empty:
                pass
            except Exception as e:
                self.logger.error(f"Error whilst processing item ({item}): {e!r}")
            sleep(self.frequency)
