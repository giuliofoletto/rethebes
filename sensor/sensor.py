"""
Module that uses LibreHardwareMonitor to read status of CPU.

Authors: Giulio Foletto.
"""
import datetime
import time
import sys
import csv
import clr
from .cpu import CPU
from instrument import Instrument

OUTPUT_DIR = "./output/"

class Sensor(Instrument):
    def __init__(self, name, configuration, context):
        super().__init__(name, configuration, context)
        self.sampling_interval = self.configuration["sampling_interval"]
        self.start_time = time.time()
        self.file = open(OUTPUT_DIR + self.configuration["file_name"], "w", newline="")
        self.writer = csv.writer(self.file, delimiter=',')
        self.header_written = False

        if "lhm_path" in self.configuration:
            sys.path.append(self.configuration["lhm_path"])
        clr.AddReference('LibreHardwareMonitorLib')
        from LibreHardwareMonitor import Hardware
        
        self.pc = Hardware.Computer()
        self.pc.IsCpuEnabled=True
        self.pc.Open()
        self.cpu = CPU(self.pc.Hardware[0])

        self.prepare_and_run()

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
    
    def send_data(self, data):
        event = dict()
        event["sender"] = self.name
        event["header"] = "sensor-data"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = data
        self.socket.send_json(event)

    def process_message(self, message):
        if "command" in message["body"] and message["body"]["command"] == "finish":
            self.should_continue = False
            self.send_event(command = "finish")
