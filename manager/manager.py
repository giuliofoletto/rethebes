"""
Core logic singlet.

Authors: Giulio Foletto.
"""

from threading import Thread
import datetime
import zmq
from loader import Loader
from sensor import Sensor
from logger import Logger

class Manager():
    def __init__(self, configuration):
        self.context = zmq.Context(0)
        self.polling_wait_time = 0.1 # seconds

        # Preprocess configuration
        self.configuration = configuration
        # Allow auto setting of file name
        if "file_name" not in self.configuration["sensor"] or self.configuration["sensor"]["file_name"] == "auto":
            self.configuration["sensor"]["file_name"] = datetime.datetime.now().isoformat(sep = "-", timespec="seconds").replace(":", "-") + ".csv"

        self.holders = dict()
        self.holders["loader"] = Holder(Loader, "loader", self.configuration["loader"], self.context)
        self.holders["sensor"] = Holder(Sensor, "sensor", self.configuration["sensor"], self.context)
        self.holders["logger"] = Holder(Logger, "logger", self.configuration["logger"], self.context)

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
            events = self.poller.poll(self.polling_wait_time*1000)
            for event in events:
                if event[0] in [v.socket for _, v in self.holders.items()]:
                    message = event[0].recv_json()
                    self.process_message(message)

    def send_event(self, **kwargs):
        event = dict()
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

class Holder():
    def __init__(self, instrument_class, name, configuration, context):
        self.instrument_class = instrument_class
        self.name = name
        self.configuration = configuration
        self.context = context
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.bind("inproc://manager-" + self.name)

    def __del__(self):
        self.running = False
        self.thread.join()
        self.socket.close()
        # Call destructor of instrument
        del self.instrument

    def launch(self):
        self.instrument = self.instrument_class(self.name, self.configuration, self.context)

    def spawn(self):
        self.thread = Thread(target=self.launch)
        self.running = True
        self.thread.start()