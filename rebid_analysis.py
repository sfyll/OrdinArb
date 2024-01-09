from typing import List
import os
from encoding.decode import decode

from dataclasses import dataclass, field

from bitcoin.core import CTransaction, CTxIn

@dataclass
class TransactionData:
    original_tx: CTransaction
    updated_txs: List[CTransaction] = field(default_factory=list)
    gas_fees: List[int] = field(default_factory=list)  # Assuming gas fees are represented as integers
    #timestamps: List[int] = field(default_factory=list)  # Assuming timestamps are Unix timestamps

    def add_update(self, tx: CTransaction, gas_fee: int, timestamp: int):
        self.updated_txs.append(tx)
        self.gas_fees.append(gas_fee)
       # self.timestamps.append(timestamp)


class MempoolAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        # Using a dictionary to store transactions with outputs as keys
        self.transactions = {}

    def process_file(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                self.process_line(line.strip())

    def process_line(self, line):
        decoded = decode(line)
        transaction = decoded.deserialize()
        # Check if it's a raw transaction
        if self.is_raw_transaction(transaction):
            transaction: CTransaction
            self.process_transaction(transaction)

    def is_raw_transaction(self, transaction):
        # Implement logic to check if the transaction is a raw transaction
        return isinstance(transaction, CTransaction) 
    
    def process_transaction(self, transaction: CTransaction):
        outputs = self.extract_outputs(transaction)
        key = tuple(outputs)
        #timestamp = self.extract_timestamp(transaction)  # Assuming you have a method to extract timestamp

        if key not in self.transactions:
            self.transactions[key] = TransactionData(original_tx=transaction)
        elif self.can_update_gas_fee(transaction.vin):
            gas_fee = self.extract_gas_fee(transaction)     # Assuming you have a method to extract gas fee
            self.transactions[key].add_update(transaction, gas_fee)

    def extract_outputs(self, transaction: CTransaction):
        return transaction.vout

    def can_update_gas_fee(self, inputs: List[CTxIn]):
        for input in inputs:
            if not input.is_final:
                return True

    def update_transactions(self, outputs, transaction):
        # Key for the dictionary is a tuple of outputs
        key = tuple(outputs)
        if key in self.transactions:
            self.transactions[key].append(transaction)
        else:
            self.transactions[key] = [transaction]

    def get_transactions(self):
        return self.transactions


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    DUMP_FILE_PATH = os.path.join(current_dir, "data/mempool_drop.txt")
    analyzer = MempoolAnalyzer(DUMP_FILE_PATH)
    analyzer.process_file()
    print(analyzer.get_transactions())

