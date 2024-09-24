import logging
import msgpack
import socketserver
import struct

from tcp_tui.messaging import NetworkMessage, RawNetworkMessage


class RequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server, ClientMessageHandler):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.message_handler = ClientMessageHandler()
        self.message_handler.start()
        super().__init__(request, client_address, server)

    def handle(self):
        self.logger.info(f"Connection from {self.client_address} has been established")

        while True:
            # Recieve data from client
            try:
                header = self.request.recv(4)

                if len(header) < 4:
                    self.logger.info(
                        f"Connection form {self.client_address} has been closed"
                    )
                    break

                message_len = struct.unpack(">I", header)[0]
                message_data = self.request.recv(message_len)

                while len(message_data) < message_len:
                    more_data = self.request.recv(message_len - len(message_data))
                    if not more_data:
                        break
                    message_data += more_data
            except Exception as e:
                self.logger.exception(
                    f"Exception with revieving data from {self.client_address}: {e!r}"
                )
                break

            # Process data
            try:
                unpacked_message = msgpack.unpackb(message_data, raw=False)
                self.process(unpacked_message)
            except Exception as e:
                self.logger.exception(
                    f"Exception with processing data from {self.client_address}: {e!r}"
                )
        self.close()

    def process(self, data):
        try:
            message = RawNetworkMessage(**data)
            self.message_handler.put(message)
        except Exception as e:
            self.logger.exception(
                f"Exception while processing data from {self.client_address}: {e!r}"
            )

    def send(self, data: NetworkMessage):
        try:
            self.request.sendall(data.pack())
        except Exception as e:
            self.logger.exception(
                f"Exception while sending data to {self.client_address}: {e!r}"
            )

    def close(self):
        self.logger.info(f"Closing connection to {self.client_address}")
        self.message_handler.stop()
        self.request.close()
