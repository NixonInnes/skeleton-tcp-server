import logging
from socketserver import ThreadingTCPServer
import threading


class TcpServer(ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(
        self, address: str, port: int, RequestHandler: type, ClientMessageHandler: type
    ):
        super().__init__((address, port), RequestHandler)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.host = address
        self.port = port

        self.RequestHandler = RequestHandler
        self.ClientMessageHandler = ClientMessageHandler

        self._is_shutting_down = threading.Event()

    def finish_request(self, request, client_address):
        self.RequestHandler(request, client_address, self, self.ClientMessageHandler)

    def stop(self):
        self.logger.info("Server shutting down")
        self.shutdown()
        self.server_close()
        self._is_shutting_down.set()

    def start(self):
        server_thread = threading.Thread(target=self.serve_forever)
        server_thread.start()
        self.logger.info(f"Server started on {self.host}:{self.port}")

        try:
            while not self._is_shutting_down.is_set():
                pass
        except KeyboardInterrupt:
            self.logger.info("Server shutting down")
        finally:
            self.stop()
            server_thread.join()
