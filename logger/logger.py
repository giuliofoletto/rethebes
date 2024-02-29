"""
Module that logs messages sent by other modules.

Authors: Giulio Foletto.
"""

import json
from util import Instrument

class Logger(Instrument):
    def __init__(self, name, configuration, context):
        super().__init__(name, configuration, context)

    def open(self):
        print("Program starts - Press CTRL+C to exit (more or less) gracefully or CTRL+BREAK to force exit")

    def close(self):
        print("Program ends gracefully")

    def run(self):
        # logger is just a listener
        return self.listen()        

    def process_message(self, message):
        if message["header"] == "sensor-data":
            pass # Do nothing at the moment
        if message["header"] == "loader-event":
            self.log_message(message)
        elif message["header"] == "manager-event":
            super().process_message(message)
            self.log_message(message)

    def log_message(self, message):
        print(message["time"], message["header"], json.dumps(message["body"]))
