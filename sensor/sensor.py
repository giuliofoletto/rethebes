import datetime
import clr
from .cpu import CPU
import sys
sys.path.append("./sensor/lib")
clr.AddReference('LibreHardwareMonitorLib')
from LibreHardwareMonitor import Hardware
import time
import csv
import zmq

OUTPUT_DIR = "./output/"

class Sensor():

    def __init__(self, configuration, context):

        self.duration = configuration["duration"]
        self.sampling_interval = configuration["sampling_interval"]
        self.start_time = time.time()
        self.stop_time = self.start_time + self.duration
        self.file = open(OUTPUT_DIR + configuration["file_name"], "w", newline="")
        self.writer = csv.writer(self.file, delimiter=',')
        self.header_written = False

        self.context = context
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect("inproc://manager-sensor")

        self.pc = Hardware.Computer()
        self.pc.IsCpuEnabled=True
        self.pc.Open()
        self.cpu = CPU(self.pc.Hardware[0])
        

    def run(self):
        while(time.time() < self.stop_time):
            stop_period = time.time() + self.sampling_interval
            values = {"Time": datetime.datetime.now().isoformat()}
            values.update(self.cpu.read())
            if not self.header_written:
                self.writer.writerow(list(values.keys()))
                self.header_written = True
            self.writer.writerow(list(values.values()))
            self.send_data(values)
            time.sleep(max(0, stop_period-time.time()))

    def send_data(self, data):
        event = dict()
        event["header"] = "sensor-data"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = data
        self.socket.send_json(event)

