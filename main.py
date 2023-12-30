
from networking.zmq_handler.zmq_sub import ZMQHandler
from networking.zmq_handler.zmq_handlers import PrintHandler, WriteToFileHandler, MultiHandler

DUMP_FILE_PATH = "dump/dump.txt"

if __name__ == '__main__':

    message_handler = MultiHandler([
        PrintHandler(),
        WriteToFileHandler(DUMP_FILE_PATH)
    ])

    print("Starting ZMQHandler")
    zmqHandler = ZMQHandler(
        message_handler=message_handler
    )
    zmqHandler.start()
