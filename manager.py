from threading import Thread
from loader import Loader
from sensor import Sensor
from logger import Logger
import queue
import datetime

class Manager():
    def __init__(self, configuration):
        self.event_queue = queue.Queue()

        # Preprocess configuration
        self.configuration = configuration
        # Allow auto setting of duration for slave objects
        master_duration = 0
        for load in self.configuration["loader"]:
            master_duration += load["duration"]
        for slave in ["sensor", "logger"]:
            if "duration" not in self.configuration[slave] or self.configuration[slave]["duration"] == "auto":
                self.configuration[slave]["duration"] = master_duration

        self.loader = Loader(self.configuration["loader"], self.event_queue)
        self.t_loader = Thread(target = self.loader.run)
        self.t_loader.start()

        self.sensor = Sensor(self.configuration["sensor"], self.event_queue)
        self.t_sensor = Thread(target = self.sensor.run)
        self.t_sensor.start()

        self.logger = Logger(self.configuration["logger"], self.event_queue)
        self.t_logger = Thread(target = self.logger.run)
        self.t_logger.start()

    def send_event(self, **kwargs):
        event = dict()
        event["header"] = "manager-event"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = kwargs
        self.event_queue.put(event)