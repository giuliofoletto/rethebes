"""
Class that implements a basic timer instruments, which essentially stops others after some time.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import logging
import time

from rethebes.instrulib import Instrument


class Timer(Instrument):
    def __init__(self, name, context, configuration):
        self.configuration = configuration
        self.first_run = True
        super().__init__(name, context)

    def run(self):
        if self.configuration["duration"] < 0:  # infinite run
            if self.first_run:
                logging.info(
                    "Starting infinite acquisition. Must be stopped with CTRL+C."
                )
                self.first_run = False
            self.listen()
        else:
            if self.first_run:
                logging.info(
                    "Starting timer for "
                    + str(self.configuration["duration"])
                    + " seconds"
                )
                self.stop_time = time.time() + self.configuration["duration"]
                self.first_run = False
            self.listen((self.stop_time - time.time()) * 1000)  # Conversion to ms
            if time.time() > self.stop_time:
                self.send_event(command="finish")
                self.set_state("waiting")
