
from bitcoin.core import CTransaction

# Examples:
# TransactionHash(sequence=564091, tx_hash=662038688ad4727bcbc7d9f5fb3635279435ac83d86d28daa30a4e28aa78e52b)
# RawTransaction(sequence=564091, raw_tx=010000000001019ea7727841f5406dcf219691f3eeeb4d36a775720ba3ec269d33f1c9667638710000000000ffffffff02df11160000000000160014bf9b43b1a62ffcd7edcf336e0d770f7e70971a67a528020000000000160014195d08ab5c31a852319eba303116a537cc45681402483045022100b6b575fa4fdbae86f4f650dac21bc07a4551bf50e000c810068377f7771342d002205a7683aa6ac9f57899e21062bd3475b355d7c5eb170a17f40f7d36613a595d9b01210343c697a0f53f530f064ad7b3eef2f00e4b48b7f24c828b30c2c593574289aa7a00000000)


class RawTransaction:
    def __init__(self, sequence: int, raw_tx: str):
        self.sequence = sequence
        self.raw_tx = raw_tx

    def encode(self):
        return "RawTransaction(sequence={}, raw_tx={})".format(self.sequence, self.raw_tx)

    def decode(self, encoded):
        sequence, raw_tx = encoded.split(",")
        self.sequence = int(sequence.split("=")[1])
        self.raw_tx = raw_tx.split("=")[1][:-1]

    def deserialize(self):
        return CTransaction.deserialize(bytes.fromhex(self.raw_tx))


class TransactionHash:
    def __init__(self, sequence: int, raw_tx: str):
        self.sequence = sequence
        self.raw_tx = raw_tx

    def encode(self):
        return "TransactionHash(sequence={}, tx_hash={})".format(self.sequence, self.raw_tx)

    def decode(self, encoded):
        sequence, raw_tx = encoded.split(",")
        self.sequence = int(sequence.split("=")[1])
        self.raw_tx = raw_tx.split("=")[1][:-1]


def decode(encoded: str):
    if encoded.startswith("RawTransaction"):
        tx = RawTransaction(0, "")
        tx.decode(encoded)
        return tx
    elif encoded.startswith("TransactionHash"):
        tx = TransactionHash(0, "")
        tx.decode(encoded)
        return tx
    else:
        raise Exception("Unknown type: {}".format(encoded))


if __name__ == "__main__":

    TRANSACTION_HASH_TEST = "TransactionHash(sequence=564091, tx_hash=662038688ad4727bcbc7d9f5fb3635279435ac83d86d28daa30a4e28aa78e52b)"
    RAW_TRANSACTION_TEST = "RawTransaction(sequence=564091, raw_tx=010000000001019ea7727841f5406dcf219691f3eeeb4d36a775720ba3ec269d33f1c9667638710000000000ffffffff02df11160000000000160014bf9b43b1a62ffcd7edcf336e0d770f7e70971a67a528020000000000160014195d08ab5c31a852319eba303116a537cc45681402483045022100b6b575fa4fdbae86f4f650dac21bc07a4551bf50e000c810068377f7771342d002205a7683aa6ac9f57899e21062bd3475b355d7c5eb170a17f40f7d36613a595d9b01210343c697a0f53f530f064ad7b3eef2f00e4b48b7f24c828b30c2c593574289aa7a00000000)"

    tx_hash = decode(TRANSACTION_HASH_TEST)
    raw_tx = decode(RAW_TRANSACTION_TEST)
    deserialized_tx = raw_tx.deserialize()

    print("transaction hash: {}".format(tx_hash.raw_tx))
    print("raw transaction: {}".format(raw_tx.raw_tx))
    print("deserialized transaction: {}".format(deserialized_tx))
