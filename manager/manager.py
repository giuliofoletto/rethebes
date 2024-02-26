"""
Core logic singlet.

Authors: Giulio Foletto.
"""

import datetime
import zmq
from util import Holder

OUTPUT_DIR = "./output/"

class Manager():
    def __init__(self, configuration):
        self.context = zmq.Context(0)
        self.polling_wait_time = 0.1 # seconds

        # Preprocess configuration
        self.configuration = configuration
        # Allow auto setting of file name
        if "file_name" not in self.configuration["sensor"] or self.configuration["sensor"]["file_name"] == "auto":
            self.configuration["sensor"]["file_name"] = OUTPUT_DIR + datetime.datetime.now().isoformat(sep = "-", timespec="seconds").replace(":", "-") + ".csv"

        self.holders = dict()
        for instrument in self.configuration:
            self.holders[instrument] = Holder(instrument, self.configuration[instrument], self.context)

        for _, v in self.holders.items():
            v.spawn()

        self.poller = zmq.Poller()
        for s in [v.socket for _, v in self.holders.items()]:
            self.poller.register(s, zmq.POLLIN)

        self.should_continue = True
        self.listen()

    def __del__(self):
        # Call destructors of holders
        self.holders.clear()
        self.context.term()

    def listen(self):
        while self.check_should_continue():
            try:
                events = self.poller.poll(self.polling_wait_time*1000)
            except KeyboardInterrupt:
                self.send_event(command = "finish")
                events = []
            for event in events:
                if event[0] in [v.socket for _, v in self.holders.items()]:
                    message = event[0].recv_json()
                    self.process_message(message)

    def send_event(self, **kwargs):
        event = dict()
        event["sender"] = "manager"
        event["header"] = "manager-event"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = kwargs
        for socket in [v.socket for _, v in self.holders.items()]:
            socket.send_json(event)
    
    def process_message(self, message):
        if "-event" in message["header"] and message["body"]["command"] == "finish":
            if message["sender"] == "loader":
                self.send_event(command = "finish")
            self.holders[message["sender"]].running = False
        if self.check_should_continue():
            self.holders["logger"].socket.send_json(message)

    def check_should_continue(self):
        condition = False
        for c in [v.running for _, v in self.holders.items()]:
            condition = condition or c
        self.should_continue = condition
        return self.should_continue
