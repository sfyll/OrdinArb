import struct

from networking.zmq_handler.zmq_objects import TransactionHash, RawBlock, RawTransaction, RawBlock, SequenceNumber, Label 

"""
    ZMQ example using python3's asyncio

    Bitcoin should be started with the command line arguments:
        bitcoind -testnet -daemon \
                -zmqpubrawtx=tcp://127.0.0.1:28332 \
                -zmqpubrawblock=tcp://127.0.0.1:28332 \
                -zmqpubhashtx=tcp://127.0.0.1:28332 \
                -zmqpubhashblock=tcp://127.0.0.1:28332 \
                -zmqpubsequence=tcp://127.0.0.1:28332

    We use the asyncio library here.  `self.handle()` installs itself as a
    future at the end of the function.  Since it never returns with the event
    loop having an empty stack of futures, this creates an infinite loop.  An
    alternative is to wrap the contents of `handle` inside `while True`.

    A blocking example using python 2.7 can be obtained from the git history:
    https://github.com/bitcoin/bitcoin/blob/37a7fe9e440b83e2364d5498931253937abe9294/contrib/zmq/zmq_sub.py
"""

import asyncio
import zmq
import zmq.asyncio
import signal
import struct
import sys

if (sys.version_info.major, sys.version_info.minor) < (3, 5):
    print("This example only works with Python 3.5 and greater")
    sys.exit(1)

port = 28332

class ZMQHandler():
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.zmqContext = zmq.asyncio.Context()
        self.sequence = 0
        self.zmqSubSocket = self.zmqContext.socket(zmq.SUB)
        self.zmqSubSocket.setsockopt(zmq.RCVHWM, 0)
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "hashblock")
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "hashtx")
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "rawblock")
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "rawtx")
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "sequence")
        self.zmqSubSocket.connect("tcp://127.0.0.1:%i" % port)

    async def handle(self):
        topic, body, seq = await self.zmqSubSocket.recv_multipart()
        decoded_message = self.decode_message(topic, body, seq)
                
        # Process the decoded message
        print(decoded_message)
        
        # Schedule the next receive
        asyncio.ensure_future(self.handle())

    def decode_message(self, topic: bytes, body: bytes, seq: bytes) -> object:
        # Convert the sequence bytes to an integer
        sequence = -1  # Default to -1 if sequence cannot be unpacked
        if len(seq) == 4:
            sequence = struct.unpack('<I', seq)[0]
        
        # Decode the message based on the topic
        if topic == b"hashblock":
            return BlockHash(sequence=sequence, block_hash=body.hex())
        elif topic == b"hashtx":
            return TransactionHash(sequence=sequence, tx_hash=body.hex())
        elif topic == b"rawblock":
            return RawBlock(sequence, body[:80].hex())  # Assuming the header is 80 bytes
        elif topic == b"rawtx":
            return RawTransaction(sequence, body.hex())
        elif topic == b"sequence":
            hash = body[:32].hex()
            label = chr(body[32])
            label_enum = Label.from_char(label)
            mempool_sequence = None if len(body) != 32+1+8 else struct.unpack("<Q", body[32+1:])[0]
            return SequenceNumber(sequence, hash, label_enum, mempool_sequence)
        else:
            raise ValueError("Unknown topic")

    def start(self):
        self.loop.add_signal_handler(signal.SIGINT, self.stop)
        self.loop.create_task(self.handle())
        self.loop.run_forever()

    def stop(self):
        self.loop.stop()
        self.zmqContext.destroy()

daemon = ZMQHandler()
daemon.start()
