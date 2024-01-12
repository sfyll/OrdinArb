import csv
import hashlib
from typing import Dict, List, Union
import os 
from encoding.decode import BlockHash, RawTransaction, TransactionHash, decode
from networking.zmq_handler.zmq_objects import BlockHash as ZmqBlockHash, RawTransaction as ZmqRawTransaction, TransactionHash as ZmqTransactionHash

from dataclasses import dataclass, field

from bitcoin.core import CTransaction, CTxIn,  CTxOut, lx, b2x, Hash
from bitcoin.rpc import Proxy 

@dataclass
class TransactionData:
    txs: List[CTransaction]
    gas_fees: List[int] = field(default_factory=list)  # Assuming gas fees are represented as integers
    timestamps: List[int] = field(default_factory=list)  # Assuming timestamps are Unix timestamps

    def add_update(self, tx: CTransaction,  gas_fee: int, timestamp):
        self.txs.append(tx)
        self.gas_fees.append(gas_fee)
        self.timestamps.append(timestamp)


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
        self.client = Proxy(btc_conf_file=os.path.join(file_path, "networking/.env"))
        self.input_file_path = os.path.join(file_path, "data/mempool_drop.txt")
        self.output_file_path = os.path.join(file_path, "data/rebid_output.csv")
        self.current_block: int = self.client.getblockcount()
        self.transactions = {}
        self.value_per_prevout_cache: Dict[str, int] = {}
        self.tx_meta_data_per_hash: Dict[str, TxMetaData] = {}
    
    
    def handle(self, message):
        if self.is_zmq_raw_transaction(message):
            transaction = RawTransaction(message.sequence, message.raw_tx, message.timestamp)
            self.process_transaction(transaction.deserialize(), transaction.timestamp.timestamp())
        elif self.is_zmq_hash_block(message):
            self.dump_block_transactions()
            self.update_block_number()

    #Assumes that the lines are ordered by arrival time
    def process_file(self):
        with open(self.input_file_path, 'r') as file:
            for idx, line in enumerate(file):
                cached_block_number = self.current_block
                self.process_line(line.strip())
                if cached_block_number != self.current_block:
                    return

    def process_line(self, line):
        decoded = decode(line)
        # Check if it's a raw transaction
        if self.is_raw_transaction(decoded):
            self.process_transaction(decoded.deserialize(), decoded.timestamp.timestamp())
        elif self.is_hash_transaction(decoded):
            pass
        elif self.is_hash_block(decoded):
            self.dump_block_transactions()
            self.update_block_number()

    def is_zmq_raw_transaction(self, transaction):
        # Implement logic to check if the transaction is a raw transaction
        return isinstance(transaction, ZmqRawTransaction) 

    def is_zmq_hash_transaction(self, transaction):
        return isinstance(transaction, ZmqTransactionHash) 
    
    def is_zmq_hash_block(self, block):
        return isinstance(block, ZmqBlockHash) 
    
    def is_raw_transaction(self, transaction):
        # Implement logic to check if the transaction is a raw transaction
        return isinstance(transaction, RawTransaction) 

    def is_hash_transaction(self, transaction):
        return isinstance(transaction, TransactionHash) 
    
    def is_hash_block(self, block):
        return isinstance(block, BlockHash) 
   
    def process_transaction(self, transaction: CTransaction, timestamp: int):
        key = self.get_key_from_inputs(transaction.vin)

        if key not in self.transactions:
            if self.can_update_gas_fee(transaction.vin):
                input_value = self.extract_input_value(transaction)     
                gas_fee = input_value - self.get_gas_fees_from_outputs(transaction.vout)
                self.transactions[key] = TransactionData(txs=[transaction], gas_fees=[gas_fee], timestamps=[timestamp])
                print(f"adding RBF transaction with gas fee {gas_fee} ")
        else:
            input_value = self.extract_input_value(transaction)     
            gas_fee = input_value - self.get_gas_fees_from_outputs(transaction.vout) 
            self.transactions[key].add_update(transaction, gas_fee, timestamp)
            print(f"------------------------------------------------------")
            print(f"UPDATING RBF transaction with gas fee {gas_fee} !!!!")
            print(f"------------------------------------------------------")
    
    def get_key_from_inputs(self, inputs: CTxIn):
        concatenated_hashes = ''.join([input.prevout.hash.hex() + str(input.prevout.n) for input in inputs])
        return hashlib.sha256(concatenated_hashes.encode()).hexdigest()

    def get_key_from_input(self, prevout_hash: bytes, prevout_n: int):
        return hashlib.sha256((prevout_hash.hex() + str(prevout_n)).encode()).hexdigest()
    
    def process_hash_transaction(self, transaction_hash: str):
        #timestamp = self.extract_timestamp(transaction)  # Assuming you have a method to extract timestamp
    
        tx_meta_data = self.get_tx_meta_data(transaction_hash)

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
 
    def dump_block_transactions(self):
        # Check if the file exists to determine if we need to write headers
        file_exists = os.path.isfile(self.output_file_path)
        
        with open(self.output_file_path, mode='w', newline='') as file:  # 'a' opens the file in append mode
            writer = csv.writer(file)
            
            # Write headers only if the file did not exist
            if not file_exists:
                #externalTransactionId matches what you'll find on blockexplorer
                #internalTransactionId is generated only looking at inputs, despites generating a less strict hash than the standard procedure (and more likely to have collision)
                writer.writerow(['externaltransactionId','internalTransactionId', 'gasFee', 'timestamp', 'blockId'])

            for key, tx_data in self.transactions.items():
                if len(tx_data.gas_fee) > 2:
                    final_tx = tx_data.txs[-1]
                    for gas_fee, timestamp in zip(tx_data.gas_fees, tx_data.timestamps):
                        # Assuming you have a method to determine the blockId and sender
                        writer.writerow([lx(final_tx.GetTxid().hex()).hex(), key, gas_fee, timestamp, self.current_block])
        
        self.reset_cache()
    
    def update_block_number(self):
        latest_block = self.client.getblockcount()
        if self.current_block + 1 == latest_block:
            self.current_block += 1
        else:
            raise ValueError("Block update not sequential, not handling that case for now")
    
    def reset_cache(self):
        self.transactions = {}
        self.value_per_prevout_cache: Dict[str, int] = {}
        self.tx_meta_data_per_hash: Dict[str, TxMetaData] = {}


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    analyzer = MempoolAnalyzer(current_dir)
    analyzer.process_file()

