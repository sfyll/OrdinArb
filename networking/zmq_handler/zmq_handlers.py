import os

from rebid_analysis import MempoolAnalyzer

class PrintHandler():
    def __init__(self):
        pass

    def handle(self, message):
        print(message)


class WriteToFileHandler():
    def __init__(self, filename: str):
        self.filename = filename
        # check if file exists and if not create it
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        self.file = open(filename, "w")

    def handle(self, message):
        self.file.write(str(message) + "\n")
        self.file.flush()


class MultiHandler():
    def __init__(self, handlers: list):
        self.handlers = handlers

    def handle(self, message):
        for handler in self.handlers:
            handler.handle(message)

class RebidHandler():
    def __init__(self, root_directory) -> None:
        self.handler = MempoolAnalyzer(root_directory) 

    def handle(self, message):
        self.handler.handle(message) 
