"""
Core logic singlet.

Authors: Giulio Foletto.
"""

from rethebes.util import Director

class Manager(Director):
    def process_message(self, message):
        if "-event" in message["header"] and message["body"]["command"] == "finish":
            if message["sender"] == "loader":
                self.send_event(command = "close")
                self.wait_for_closure()
        else:
            super().process_message(message)