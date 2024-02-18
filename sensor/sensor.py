import datetime
import clr
from .cpu import CPU
import sys
sys.path.append("./sensor/lib")
clr.AddReference('LibreHardwareMonitorLib')
from LibreHardwareMonitor import Hardware
import time

class Sensor():

    def __init__(self, configuration, event_queue):

        self.duration = configuration["duration"]
        self.sampling_interval = configuration["sampling_interval"]
        self.start_time = time.time()
        self.stop_time = self.start_time + self.duration

        self.event_queue = event_queue

        self.pc = Hardware.Computer()
        self.pc.IsCpuEnabled=True
        self.pc.Open()
        self.cpu = CPU(self.pc.Hardware[0])
        

    def run(self):
        while(time.time() < self.stop_time):
            stop_period = time.time() + self.sampling_interval
            values = {"Time": datetime.datetime.now().isoformat()}
            values.update(self.cpu.read())
            self.send_data(values)
            time.sleep(max(0, stop_period-time.time()))

    def send_data(self, data):
        event = dict()
        event["header"] = "sensor-data"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = data
        self.event_queue.put(event)
