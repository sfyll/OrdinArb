import hashlib
from typing import Dict, List, Union
import os
from encoding.decode import decode

from dataclasses import dataclass, field

from bitcoin.core import CTransaction, CTxIn, CTxInWitness, CTxOut, Hash, lx
from bitcoin.rpc import Proxy 

@dataclass
class TransactionData:
    original_tx: CTransaction
    gas_fees: List[int] = field(default_factory=list)  # Assuming gas fees are represented as integers
    #timestamps: List[int] = field(default_factory=list)  # Assuming timestamps are Unix timestamps

    def add_update(self, gas_fee: int, timestamp = None):
        self.gas_fees.append(gas_fee)
       # self.timestamps.append(timestamp)


@dataclass
class TxMetaData:
    txHash: str
    size: int
    vsize: int
    weight: int
    blockhash: str
    confirmations: int
    time: int
    blocktime: int
    tx: CTransaction


class MempoolAnalyzer:
    def __init__(self, file_path):
        self.client = Proxy(btc_conf_file=os.path.join(current_dir, "networking/.env"))
        self.file_path = os.path.join(file_path, "data/mempool_drop.txt")
        # Using a dictionary to store transactions with outputs as keys
        self.transactions = {}
        self.value_per_prevout_cache: Dict[str, int] = {}
        self.tx_meta_data_per_hash: Dict[str, TxMetaData] = {}
    
    #Assumes that the lines are ordered by arrival time
    def process_file(self):
        with open(self.file_path, 'r') as file:
            for idx, line in enumerate(file):
                self.process_line(line.strip())

    def process_line(self, line):
        decoded = decode(line)
        try:
            transaction = decoded.deserialize()
        #hacky way to bypass non implemented stuff
        except AttributeError:
            return
        # Check if it's a raw transaction
        if self.is_raw_transaction(transaction):
            self.process_transaction(transaction)
        elif self.is_hash_transaction(transaction):
            print(transaction)
        #    self.process_hash_transaction(transaction)
        #else:
        #    raise NotImplementedError

    def is_raw_transaction(self, transaction):
        # Implement logic to check if the transaction is a raw transaction
        return isinstance(transaction, CTransaction) 

    def is_hash_transaction(self, transaction):
        return isinstance(transaction, str) and len(transaction) == 64
    
    def process_transaction(self, transaction: CTransaction):
        key = self.get_key_from_inputs(transaction.vin)
        #timestamp = self.extract_timestamp(transaction)  # Assuming you have a method to extract timestamp
        
        if key not in self.transactions:
            if self.can_update_gas_fee(transaction.vin):
                input_value = self.extract_input_value(transaction)     # Assuming you have a method to extract gas fee
                gas_fee = input_value - self.get_gas_fees_from_outputs(transaction.vout)
                self.transactions[key] = TransactionData(original_tx=transaction, gas_fees=[gas_fee])
                print(f"adding RBF transaction with gas fee {gas_fee} ")
        else:
            input_value = self.extract_input_value(transaction)     # Assuming you have a method to extract gas fee
            gas_fee = input_value - self.get_gas_fees_from_outputs(transaction.vout) 
            self.transactions[key].add_update(gas_fee)
            print(f"------------------------------------------------------")
            print(f"------------------------------------------------------")
            print(f"------------------------------------------------------")
            print(f"------------------------------------------------------")
            print(f"------------------------------------------------------")
            print(f"------------------------------------------------------")
            print(f"UPDATING RBF transaction with gas fee {gas_fee} !!!!")
            print(f"------------------------------------------------------")
            print(f"------------------------------------------------------")
            print(f"------------------------------------------------------")
            print(f"------------------------------------------------------")
            print(f"------------------------------------------------------")
            print(f"------------------------------------------------------")
            print(f"------------------------------------------------------")
    
    def get_key_from_inputs(self, inputs: CTxIn):
        concatenated_hashes = ''.join([input.prevout.hash.hex() + str(input.prevout.n) for input in inputs])
        return hashlib.sha256(concatenated_hashes.encode()).hexdigest()

    def get_key_from_input(self, prevout_hash: bytes, prevout_n: int):
        return hashlib.sha256((prevout_hash.hex() + str(prevout_n)).encode()).hexdigest()
    
    def process_hash_transaction(self, transaction_hash: str):
        #timestamp = self.extract_timestamp(transaction)  # Assuming you have a method to extract timestamp
    
        print(f"{transaction_hash}")

        tx_meta_data = self.get_tx_meta_data(transaction_hash)

        print(tx_meta_data)

        raise

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
            key = self.get_key_from_input(input.prevout.hash, input.prevout.n)
            if not key in self.value_per_prevout_cache:
                if not input.prevout.hash.hex() in self.tx_meta_data_per_hash:
                    print("querying the node")
                    print(f"{(input.prevout.hash.hex(), input.prevout.n)}")
                    self.tx_meta_data_per_hash[input.prevout.hash.hex()] = self.get_tx_meta_data_from_hash(input.prevout.hash)
                self.value_per_prevout_cache[key] = self.tx_meta_data_per_hash[input.prevout.hash.hex()].tx.vout[input.prevout.n].nValue 
            input_sum_value += self.value_per_prevout_cache[key]   
        return input_sum_value
    
    def get_tx_meta_data_from_hash(self, tx_hash: Union[str, bytes]):
        if isinstance(tx_hash, str): 
            tx_data = self.client.getrawtransaction(lx(tx_hash), True)
        elif isinstance(tx_hash, bytes):
            tx_data = self.client.getrawtransaction(tx_hash, True)
        tx_data["txHash"] = tx_data.pop("hash")

        return TxMetaData(**tx_data)

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

