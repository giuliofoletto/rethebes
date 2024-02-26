from threading import Thread
import zmq
from loader import Loader
from sensor import Sensor
from logger import Logger

class Holder():
    def __init__(self, name, configuration, context):
        self.instrument_class = self.factory(name)
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

    def factory(self, name):
        if name == "loader":
            return Loader
        elif name == "sensor":
            return Sensor
        elif name == "logger":
            return Logger
        else:
            raise ValueError("Unknown instrument")