import os
import sys
from networking.zmq_handler.zmq_sub import ZMQHandler
from networking.zmq_handler.zmq_handlers import PrintHandler, WriteToFileHandler, MultiHandler

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Default file name
default_file_name = "data/mempool_drop.txt"

# Check if a different path was provided as an argument
if len(sys.argv) > 1:
    dump_file_path = sys.argv[1]
else:
    dump_file_path = os.path.join(current_dir, default_file_name)

if __name__ == '__main__':
    message_handler = MultiHandler([
        PrintHandler(),
        WriteToFileHandler(dump_file_path)
    ])

    print("Starting ZMQHandler")
    zmqHandler = ZMQHandler(
        message_handler=message_handler,
        sub_topic=["hashtx","rawtx","hashblock"] 
    )
    zmqHandler.start()

