from typing import Dict, List
import os
from encoding.decode import decode

from dataclasses import dataclass, field

from bitcoin.core import CTransaction, CTxIn, CTxInWitness
from bitcoin.rpc import Proxy

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
        self.client = Proxy('127.0.0.1', 8332, os.path.join(current_dir, "networking/.env"))
        self.file_path = os.path.join(file_path, "data/mempool_drop.txt")
        # Using a dictionary to store transactions with outputs as keys
        self.transactions = {}
        self.value_per_prevout_cache: Dict[tuple, int] = {}

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
            input_value = self.extract_input_value(transaction)     # Assuming you have a method to extract gas fee
            gas_fee = input_value - transaction.vout.nValue
            self.transactions[key].add_update(transaction, gas_fee)

    def extract_outputs(self, transaction: CTransaction):
        return transaction.vout

    def can_update_gas_fee(self, inputs: List[CTxIn]):
        for input in inputs:
            if not input.is_final:
                return True
    
    #Please note this assume inputs are fixed.
    def extract_input_value(self, transaction: CTransaction):
        input_sum_value: int = 0
        for input in transaction.vin:
            input: CTxIn
            if (input.prevout.hash, input.prevout.n) in self.value_per_prevout_cache:
                continue
            else:
                previous_transaction: CTransaction = self.client.getrawtransaction(input.prevout.hash).deserialize()
                previous_transaction_referred_input = previous_transaction.vout.nValue
                input_sum_value += previous_transaction_referred_input
                self.value_per_prevout_cache[(input.prevout.hash, input.prevout.n)] = previous_transaction_referred_input

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
    base_file_path = os.path.join(current_dir, "data/mempool_drop.txt")
    analyzer = MempoolAnalyzer(base_file_path)
    analyzer.process_file()
    print(analyzer.get_transactions())

