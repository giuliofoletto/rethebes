"""
The director of the instruments used by rethebes.

Authors: Giulio Foletto.
License: See project-level license file.
"""

from rethebes.instrulib import Director


class Manager(Director):
    def __init__(self, name, context, subordinates, master):
        self.master = master
        super().__init__(name, context, subordinates)

    def process_message(self, message):
        if "-event" in message["header"] and message["body"]["command"] == "finish":
            if message["sender"] == self.master:
                self.send_event(command="close")
                self.wait_for_closure()
        else:
            super().process_message(message)
