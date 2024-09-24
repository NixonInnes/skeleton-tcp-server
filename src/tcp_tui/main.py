import logging

from tcp_tui.services.tcp_server import TcpServer
from tcp_tui.services.request_handler import RequestHandler
from tcp_tui.services.message_handler import MessageHandler


class Server:
    def __init__(
        self,
        address="localhost",
        port=8000,
        TcpServer: type[TcpServer] = TcpServer,
        RequestHandler: type[RequestHandler] = RequestHandler,
        MessageHandler: type[MessageHandler] = MessageHandler,
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing server")
        self.is_running = False

        self.tcp_server = TcpServer(
            address=address,
            port=port,
            RequestHandler=RequestHandler,
            ClientMessageHandler=MessageHandler,
        )

    def start(self):
        self.logger.info("Starting server")
        self.is_running = True
        self.tcp_server.start()

    def stop(self):
        self.logger.info("Server stopping")
        self.is_running = False
        self.tcp_server.stop()
