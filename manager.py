from threading import Thread
from loader import Loader
from sensor import Sensor
from logger import Logger
import queue
import datetime

class Manager():
    def __init__(self, configuration):
        self.configuration = configuration
        self.event_queue = queue.Queue()

        self.loader = Loader(configuration["loader"], self.event_queue)
        self.t_loader = Thread(target = self.loader.run)
        self.t_loader.start()

        self.sensor = Sensor(configuration["sensor"], self.event_queue)
        self.t_sensor = Thread(target = self.sensor.run)
        self.t_sensor.start()

        self.logger = Logger(configuration["logger"], self.event_queue)
        self.t_logger = Thread(target = self.logger.run)
        self.t_logger.start()

    def send_event(self, **kwargs):
        event = dict()
        event["header"] = "manager-event"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = kwargs
        self.event_queue.put(event)