"""
Class that implements a basic timer instruments, which essentially stops others after some time.

Authors: Giulio Foletto.
"""

import time
import logging
from rethebes.instrulib import Instrument

class Timer(Instrument):
    def __init__(self, name, context, configuration):
        self.configuration = configuration
        self.stop_time_set = False
        super().__init__(name, context)

    def run(self):
        logging.info("Starting timer for " + str(self.configuration["duration"]) + " seconds")
        if not self.stop_time_set:
            self.stop_time = time.time() + self.configuration["duration"]
            self.stop_time_set = True
        self.listen((self.stop_time - time.time())*1000) # Conversion to ms
        if time.time() > self.stop_time:
            self.send_event(command = "finish")
            self.set_state("waiting")