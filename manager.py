from threading import Thread
from loader import Loader
from sensor import Sensor
from logger import Logger
import datetime
import zmq

class Manager():
    def __init__(self, configuration):
        self.context = zmq.Context(0)
        self.polling_wait_time = 0.1 # seconds

        # Preprocess configuration
        self.configuration = configuration
        # Allow auto setting of duration for slave objects
        master_duration = 0
        for load in self.configuration["loader"]:
            master_duration += load["duration"]
        for slave in ["sensor", "logger"]:
            if "duration" not in self.configuration[slave] or self.configuration[slave]["duration"] == "auto":
                self.configuration[slave]["duration"] = master_duration
        # Allow auto setting of file name
        if "file_name" not in self.configuration["sensor"] or self.configuration["sensor"]["file_name"] == "auto":
            self.configuration["sensor"]["file_name"] = datetime.datetime.now().isoformat(sep = "-", timespec="seconds").replace(":", "-") + ".csv"

        self.s_loader = self.context.socket(zmq.PAIR)
        self.s_loader.bind("inproc://manager-loader")
        self.loader = Loader(self.configuration["loader"], self.context)
        self.t_loader = Thread(target = self.loader.run)
        self.t_loader.start()

        self.s_sensor = self.context.socket(zmq.PAIR)
        self.s_sensor.bind("inproc://manager-sensor")
        self.sensor = Sensor(self.configuration["sensor"], self.context)
        self.t_sensor = Thread(target = self.sensor.run)
        self.t_sensor.start()

        self.s_logger = self.context.socket(zmq.PAIR)
        self.s_logger.bind("inproc://manager-logger")
        self.logger = Logger(self.configuration["logger"], self.context)
        self.t_logger = Thread(target = self.logger.run)
        self.t_logger.start()

        self.sockets = [self.s_loader, self.s_sensor, self.s_logger]

        self.should_continue = True
        self.listen()

    def listen(self):
        self.poller = zmq.Poller()
        self.poller.register(self.s_loader, zmq.POLLIN)
        self.poller.register(self.s_sensor, zmq.POLLIN)
        self.poller.register(self.s_logger, zmq.POLLIN)

        while self.should_continue:
            events = self.poller.poll(self.polling_wait_time*1000)
            for event in events:
                if event[0] in self.sockets:
                    message = event[0].recv_json()
                    self.dispatch(message)

    def send_event(self, **kwargs):
        event = dict()
        event["header"] = "manager-event"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = kwargs
        for socket in self.sockets:
            socket.send_json(event)
    
    def dispatch(self, message):
        if message["header"] == "loader-event" and message["body"]["command"] == "finish":
            self.send_event(command = "finish")
            self.should_continue = False
        self.s_logger.send_json(message)