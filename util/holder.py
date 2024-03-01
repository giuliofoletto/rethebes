from threading import Thread
import zmq

class Holder():
    def __init__(self, name, context, configuration):
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
        self.instrument = self.instrument_class(self.name, self.context, self.configuration)

    def spawn(self):
        self.thread = Thread(target=self.launch)
        self.running = True
        self.thread.start()

    def factory(self, name):
        # Ugly import logic to avoid circular imports when importing Instrument which is part of util like Holder
        if name == "loader":
            from loader import Loader
            return Loader
        elif name == "sensor":
            from sensor import Sensor
            return Sensor
        elif name == "logger":
            from logger import Logger
            return Logger
        else:
            raise ValueError("Unknown instrument")