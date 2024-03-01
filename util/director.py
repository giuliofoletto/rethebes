"""
???

Authors: Giulio Foletto.
"""

import logging
import json
import zmq
from util import Instrument

class Director(Instrument):
    def __init__(self, name, context, subordinates = []):
        self.subordinates = subordinates
        self.threads = dict()
        super().__init__(name, context)

    def join(self):
        self.terminate_sockets()
        self.threads.clear()
        self.subordinates.clear()

    def init_sockets(self):
        self.poller = zmq.Poller()
        self.sockets = dict()
        for subordinate in self.subordinates:
            socket = self.context.socket(zmq.PAIR)
            socket.bind("inproc://" + subordinate.name)
            self.sockets[subordinate.name] = socket
            self.poller.register(socket, zmq.POLLIN)
        self.sockets_ready = True

    def launch(self):
        self.main()
        self.join()

    def open(self):
        for subordinate in self.subordinates:
            thread = subordinate.launch()
            self.threads[subordinate.name] = thread
        self.send_event(command = "start")
        logging.info("Program starts - Press CTRL+C to exit (more or less) gracefully or CTRL+BREAK to force exit")

    def close(self):
        for subordinate in self.subordinates:
            subordinate.join()
        logging.info("Program ends gracefully")

    def run(self):
        # Should never run
        self.set_state("waiting")

    def wait(self):
        if self.check_should_continue():
            self.listen() # Exit only with a message
        else:
            self.set_state("closing")

    def listen(self, timeout = None):
        try:
            events = self.poller.poll(timeout)
        except KeyboardInterrupt:
            self.send_event(command = "finish")
            events = []
        if len(events) > 0:
            for event in events:
                if event[0] in self.sockets.values() and event[1] == zmq.POLLIN:
                    message = event[0].recv_json()
                    self.process_message(message)

    def process_message(self, message):
        if "command" in message["body"] and message["body"]["command"] == "closing":
            self.threads[message["sender"]].join()
            self.threads.pop(message["sender"])
            self.sockets[message["sender"]].close()
            self.poller.unregister(self.sockets[message["sender"]])
            self.sockets.pop(message["sender"])

    def check_should_continue(self):
        return bool(self.threads)

class Dummy(Director):
    def process_message(self, message):
        super().process_message(message)
        if "-event" in message["header"] and message["body"]["command"] == "finish":
            if message["sender"] == "loader":
                self.send_event(command = "finish")
        if "-event" in message["header"]:
            logging.info(message["header"] + " " + json.dumps(message["body"]))