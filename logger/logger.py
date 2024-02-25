"""
Module that logs messages sent by other modules.

Authors: Giulio Foletto.
"""

import json
import datetime
import zmq

class Logger():
    def __init__(self, configuration, context):
        self.configuration = configuration
        self.context = context
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect("inproc://manager-logger")
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        self.should_continue = True
    
    def __del__(self):
        self.socket.close()

    def run(self):
        print("Program starts - Press CTRL+BREAK to force exit")
        while self.should_continue:
            self.listen()
        print("Program ends normally")

    def listen(self, timeout = None):
        events = self.poller.poll(timeout)
        if len(events) > 0:
            for event in events:
                if event[0] == self.socket and event[1] == zmq.POLLIN:
                    message = event[0].recv_json()
                    self.process_message(message)

    def process_message(self, message):
        if message["header"] == "sensor-data":
            pass # Do nothing at the moment
        if message["header"] == "loader-event":
            self.log_message(message)
        elif message["header"] == "manager-event":
            if "command" in message["body"] and message["body"]["command"] == "finish":
                self.should_continue = False
                self.send_event(command = "finish")
            self.log_message(message)

    def log_message(self, message):
        print(message["time"], message["header"], json.dumps(message["body"]))

    def send_event(self, **kwargs):
        event = dict()
        event["header"] = "logger-event"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = kwargs
        self.socket.send_json(event)