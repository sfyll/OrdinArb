from typing import Dict, List
import os
from encoding.decode import decode

from dataclasses import dataclass, field

from bitcoin.core import CTransaction, CTxIn, CTxInWitness, CTxOut
from bitcoin.rpc import Proxy

@dataclass
class TransactionData:
    original_tx: CTransaction
    gas_fees: List[int] = field(default_factory=list)  # Assuming gas fees are represented as integers
    #timestamps: List[int] = field(default_factory=list)  # Assuming timestamps are Unix timestamps

    def add_update(self, gas_fee: int, timestamp = None):
        self.gas_fees.append(gas_fee)
       # self.timestamps.append(timestamp)


class MempoolAnalyzer:
    def __init__(self, file_path):
        self.client = Proxy(btc_conf_file=os.path.join(current_dir, "networking/.env"))
        self.file_path = os.path.join(file_path, "data/mempool_drop.txt")
        # Using a dictionary to store transactions with outputs as keys
        self.transactions = {}
        self.value_per_prevout_cache: Dict[tuple, int] = {}
    
    #Assumes that the lines are ordered by arrival time
    def process_file(self):
        with open(self.file_path, 'r') as file:
            for idx, line in enumerate(file):
                print(f"line {idx}")
                self.process_line(line.strip())

    def process_line(self, line):
        decoded = decode(line)
        try:
            transaction: CTransaction = decoded.deserialize()
        #hacky way to bypass non implemented stuff
        except AttributeError:
            return
        # Check if it's a raw transaction
        if self.is_raw_transaction(transaction):
            self.process_transaction(transaction)

    def is_raw_transaction(self, transaction):
        # Implement logic to check if the transaction is a raw transaction
        return isinstance(transaction, CTransaction) 
    
    def process_transaction(self, transaction: CTransaction):
        key = tuple(transaction.vin)
        #timestamp = self.extract_timestamp(transaction)  # Assuming you have a method to extract timestamp

        if key not in self.transactions:
            if self.can_update_gas_fee(transaction.vin):
                print(key)
                input_value = self.extract_input_value(transaction)     # Assuming you have a method to extract gas fee
                gas_fee = input_value - self.get_gas_fees_from_outputs(transaction.vout)
                self.transactions[key] = TransactionData(original_tx=transaction, gas_fees=[gas_fee])
                print(f"adding RBF transaction with gas fee {gas_fee} ")
        else:
            input_value = self.extract_input_value(transaction)     # Assuming you have a method to extract gas fee
            gas_fee = input_value - self.get_gas_fees_from_outputs(transaction.vout) 
            self.transactions[key].add_update(gas_fee)
            print(f"UPDATING RBF transaction with gas fee {gas_fee}")

    def extract_outputs(self, transaction: CTransaction):
        return transaction.vout

    def can_update_gas_fee(self, inputs: List[CTxIn]):
        for input in inputs:
            if not input.is_final():
                return True
        else:
            return False
    
    #Please note this assume inputs are fixed.
    def extract_input_value(self, transaction: CTransaction) -> int:
        input_sum_value: int = 0
        for input in transaction.vin:
            input: CTxIn
            if (input.prevout.hash, input.prevout.n) in self.value_per_prevout_cache:
                input_sum_value += self.value_per_prevout_cache[(input.prevout.hash, input.prevout.n)]   
            else:
                previous_transaction: CTransaction =  self.client.getrawtransaction(input.prevout.hash)
                previous_transaction_referred_input = self.get_gas_fees_from_outputs(previous_transaction.vout) 
                input_sum_value += previous_transaction_referred_input
                self.value_per_prevout_cache[(input.prevout.hash, input.prevout.n)] = previous_transaction_referred_input

        return input_sum_value

    def get_gas_fees_from_outputs(self, outputs: tuple[CTxOut]) -> int:
        return sum(output.nValue for output in outputs)
    
    #not used for now, we will assume inputs remain constant
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
    analyzer = MempoolAnalyzer(current_dir)
    analyzer.process_file()
    print(analyzer.get_transactions())

