"""
Core logic singlet.

Authors: Giulio Foletto.
"""

import datetime
import zmq
from util import Instrument, Holder
from .default_configuration import default_configuration

OUTPUT_DIR = "./output/"

class Manager(Instrument):
    def __init__(self, configuration):
        name = "manager"
        context = zmq.Context(0)
        super().__init__(name, configuration, context)

    def init_sockets(self):
        # This does not actually initialize sockets, only warn that they are not ready yet
        self.sockets_ready = False

    def open(self):
        # Preprocess configuration
        self.pre_process_configuration()
        
        self.holders = dict()
        for instrument in self.configuration["manager"]["instruments"]:
            self.holders[instrument] = Holder(instrument, self.configuration[instrument], self.context)

        for _, v in self.holders.items():
            v.spawn()

        self.sockets = [v.socket for _, v in self.holders.items()]
        self.poller = zmq.Poller()
        for s in self.sockets:
            self.poller.register(s, zmq.POLLIN)
        self.sockets_ready = True

        self.should_execute_post_main_block = True
        self.send_event(command = "start")

    def close(self):
        if self.should_execute_post_main_block:
            if self.configuration["manager"]["analyze"]:
                from analyzer import Analyzer
                Analyzer(self.configuration["sensor"]["file_name"])

    def __del__(self):
        for s in self.sockets:
            s.close()
        # Call destructors of holders
        self.sockets.clear()
        self.holders.clear()
        self.context.term()

    def wait(self):
        if self.check_should_continue():
            self.listen(100)
        else:
            self.set_state("closing")

    def listen(self, timeout = None):
        try:
            events = self.poller.poll(timeout)
        except KeyboardInterrupt:
            self.send_event(command = "finish")
            self.should_execute_post_main_block = False
            events = []
        for event in events:
            if event[0] in self.sockets:
                message = event[0].recv_json()
                self.process_message(message)
    
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
        return condition

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
