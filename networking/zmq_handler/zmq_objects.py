from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime

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
    timestamp: datetime = field(default_factory=datetime.now)
    
    def message_type(self):
        return "Transaction Hash"

    def __post_init__(self):
        super().__init__()

@dataclass
class BlockHash(ZMQMessage):
    sequence: int
    block_hash: str
    timestamp: datetime = field(default_factory=datetime.now)

    def message_type(self):
        return "Block Hash"

    def __post_init__(self):
        super().__init__()

@dataclass
class RawTransaction(ZMQMessage):
    sequence: int
    raw_tx: str
    timestamp: datetime = field(default_factory=datetime.now)

    def message_type(self):
        return "Raw Transaction"

    def __post_init__(self):
        super().__init__()

@dataclass
class RawBlock(ZMQMessage):
    sequence: int
    raw_block: str
    timestamp: datetime = field(default_factory=datetime.now)

    def message_type(self):
        return "Raw Block"

    def __post_init__(self):
        super().__init__()

@dataclass
class SequenceNumber(ZMQMessage):
    sequence: int
    seq_hash: Label
    label: str
    mempool_sequence: int
    timestamp: datetime = field(default_factory=datetime.now)

    def message_type(self):
        return "Sequence Number"

    def __post_init__(self):
        super().__init__()
