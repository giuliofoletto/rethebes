"""
Core logic singlet.

Authors: Giulio Foletto.
"""

import logging
import json
from util import Director

class Manager(Director):
    def process_message(self, message):
        if "-event" in message["header"]:
            logging.info(message["header"] + " " + json.dumps(message["body"]))
        if "-event" in message["header"] and message["body"]["command"] == "finish":
            if message["sender"] == "loader":
                self.send_event(command = "close")
                self.wait_for_closure()