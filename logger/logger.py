"""
Module that logs messages sent by other modules.

Authors: Giulio Foletto.
"""

import json
from util import Instrument

class Logger(Instrument):
    def __init__(self, name, configuration, context):
        super().__init__(name, configuration, context)

        self.prepare_and_run()
    
    def run(self):
        print("Program starts - Press CTRL+C to exit (more or less) gracefully or CTRL+BREAK to force exit")
        while self.should_continue:
            self.listen()
        print("Program ends gracefully")

    def process_message(self, message):
        if message["header"] == "sensor-data":
            pass # Do nothing at the moment
        if message["header"] == "loader-event":
            self.log_message(message)
        elif message["header"] == "manager-event":
            if "command" in message["body"] and message["body"]["command"] == "finish":
                self.should_continue = False
                self.send_event(command = "finish")
            self.log_message(message)

    def log_message(self, message):
        print(message["time"], message["header"], json.dumps(message["body"]))
