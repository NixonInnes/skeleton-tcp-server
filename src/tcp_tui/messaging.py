from pydantic import BaseModel, Field
from typing import ClassVar, Any
import msgpack
import struct


class RawNetworkMessage(BaseModel):
    """
    Represents the raw network message structure with aliases for compact serialization.

    Attributes:
        handle (str): The message handle, aliased as "c".
        data (Dict[str, Any]): The message data, aliased as "k".
    """

    handle: str = Field(alias="c")
    data: dict[str, Any] = Field(alias="k")


class NetworkMessage(BaseModel):
    """
    Base class for network messages that provides serialization capabilities.

    Attributes:
        c (ClassVar[str]): The message type identifier. Should be set by subclasses.
    """

    c: ClassVar[str] = ""

    def pack(self) -> bytes:
        """
        Serializes the network message into bytes with a 4-byte header indicating the message length.

        Returns:
            bytes: The packed message ready for transmission.

        Raises:
            RuntimeError: If serialization fails.
        """
        try:
            # Create a RawNetworkMessage using the class variable 'c' and the instance data
            raw_msg = RawNetworkMessage(handle=self.c, data=self.model_dump())

            # Serialize the RawNetworkMessage using msgpack with aliases and binary types
            packed_msg = msgpack.packb(
                raw_msg.model_dump(by_alias=True), use_bin_type=True
            )

            # Create a 4-byte big-endian header indicating the length of the packed message
            header = struct.pack(">I", len(packed_msg))

            return header + packed_msg
        except Exception as e:
            raise RuntimeError(f"Failed to pack network message: {e}") from e
