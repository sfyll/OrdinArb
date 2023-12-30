from dataclasses import dataclass
from abc import ABC, abstractmethod

from enum import Enum


class Label(Enum):
    BLOCK_CONNECTED = 'C'
    BLOCK_DISCONNECTED = 'D'
    TX_REMOVED_NONBLOCK = 'R'
    TX_ADDED_MEMPOOL = 'A'

    @staticmethod
    def from_char(char):
        label_mapping = {
            'C': Label.BLOCK_CONNECTED,
            'D': Label.BLOCK_DISCONNECTED,
            'R': Label.TX_REMOVED_NONBLOCK,
            'A': Label.TX_ADDED_MEMPOOL
        }
        return label_mapping.get(char, None)


class ZMQMessage(ABC):

    def __str__(self):
        # Generate a nice string representation of the data class
        class_name = self.__class__.__name__
        fields = ", ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"{class_name}({fields})"

    @abstractmethod
    def message_type(self):
        # This method should be implemented by all subclasses to return the type of message
        pass


@dataclass
class TransactionHash(ZMQMessage):
    sequence: int
    tx_hash: str

    def message_type(self):
        return "Transaction Hash"


@dataclass
class BlockHash(ZMQMessage):
    sequence: int
    block_hash: str

    def message_type(self):
        return "Block Hash"


@dataclass
class RawTransaction(ZMQMessage):
    sequence: int
    raw_tx: str

    def message_type(self):
        return "Raw Transaction"


@dataclass
class RawBlock(ZMQMessage):
    sequence: int
    raw_block: str

    def message_type(self):
        return "Raw Block"


@dataclass
class SequenceNumber(ZMQMessage):
    sequence: int
    seq_hash: Label
    label: str
    mempool_sequence: int

    def message_type(self):
        return "Sequence Number"