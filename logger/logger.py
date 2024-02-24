import time
import json
import zmq

class Logger():
    def __init__(self, configuration, context):
        self.configuration = configuration
        self.context = context
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect("inproc://manager-logger")
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        self.stop_time = time.time() + configuration["duration"] + 0.1 # Some wait time for concluding messages

    def run(self):
        print("Program starts - Press CTRL+BREAK to force exit")
        while(time.time() < self.stop_time):
            events = self.poller.poll((self.stop_time - time.time())*1000)
            if len(events) == 0:
                print("Finished logging because of duration end")
            for event in events:
                if event[0] == self.socket and event[1] == zmq.POLLIN:
                    message = self.socket.recv_json()
                    if message["header"] == "sensor-data":
                        pass # Do nothing at the moment
                    if message["header"] == "loader-event":
                        self.log_message(message)
                    elif message["header"] == "manager-event":
                        self.log_message(message)


    def log_message(self, message):
        print(message["time"], message["header"], json.dumps(message["body"]))