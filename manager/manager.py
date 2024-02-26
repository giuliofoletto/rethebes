"""
Core logic singlet.

Authors: Giulio Foletto.
"""

import datetime
import zmq
from util import Holder
from .default_configuration import default_configuration

OUTPUT_DIR = "./output/"

class Manager():
    def __init__(self, configuration):
        self.context = zmq.Context(0)
        self.polling_wait_time = 0.1 # seconds

        # Preprocess configuration
        self.configuration = configuration
        self.pre_process_configuration()
        
        self.holders = dict()
        for instrument in self.configuration["manager"]["instruments"]:
            self.holders[instrument] = Holder(instrument, self.configuration[instrument], self.context)

        for _, v in self.holders.items():
            v.spawn()

        self.poller = zmq.Poller()
        for s in [v.socket for _, v in self.holders.items()]:
            self.poller.register(s, zmq.POLLIN)

        self.should_continue = True
        self.should_execute_post_main_block = True
        self.listen()

        if self.should_execute_post_main_block:
            if self.configuration["manager"]["analyze"]:
                from analyzer import Analyzer
                Analyzer(self.configuration["sensor"]["file_name"])

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
                self.should_execute_post_main_block = False
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

    def pre_process_configuration(self):
        # Allow automatic list of instruments
        if "instruments" not in self.configuration["manager"] or self.configuration["manager"]["instruments"] == "auto":
            self.configuration["manager"]["instruments"] = []
            for k in self.configuration:
                if k != "manager":
                    self.configuration["manager"]["instruments"].append(k)
        # Allow other default settings
        for k, v in default_configuration["manager"].items():
            if k not in self.configuration:
                self.configuration[k] = v
        # Allow non-specification of logger
        if "logger" not in self.configuration["manager"]["instruments"]:
            self.configuration["manager"]["instruments"].append("logger")
            self.configuration["logger"] = default_configuration["logger"]
        # Allow auto setting of file name
        if "sensor" in self.configuration and ("file_name" not in self.configuration["sensor"] or self.configuration["sensor"]["file_name"] == "auto"):
            self.configuration["sensor"]["file_name"] = OUTPUT_DIR + datetime.datetime.now().isoformat(sep = "-", timespec="seconds").replace(":", "-") + ".csv"
