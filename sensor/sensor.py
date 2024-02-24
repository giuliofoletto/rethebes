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
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        self.pc = Hardware.Computer()
        self.pc.IsCpuEnabled=True
        self.pc.Open()
        self.cpu = CPU(self.pc.Hardware[0])

        self.should_continue = True

    def run(self):
        while self.should_continue:
            self.listen(0) # Return immediately
            if not self.should_continue: # Allow stopping via message
                break
            stop_period = time.time() + self.sampling_interval
            self.act()
            time.sleep(max(0, stop_period-time.time()))

    def act(self):
        values = {"Time": datetime.datetime.now().isoformat()}
        values.update(self.cpu.read())
        if not self.header_written:
            self.writer.writerow(list(values.keys()))
            self.header_written = True
        self.writer.writerow(list(values.values()))
        self.send_data(values)
    
    def listen(self, timeout = None):
        events = self.poller.poll(timeout)
        if len(events) > 0:
            for event in events:
                if event[0] == self.socket and event[1] == zmq.POLLIN:
                    message = event[0].recv_json()
                    self.process_message(message)

    def send_data(self, data):
        event = dict()
        event["header"] = "sensor-data"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = data
        self.socket.send_json(event)

    def process_message(self, message):
        if "command" in message["body"] and message["body"]["command"] == "finish":
            self.should_continue = False
