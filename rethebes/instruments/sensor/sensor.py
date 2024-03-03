"""
Module that uses LibreHardwareMonitor to read status of CPU.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import datetime
import logging
import time
import sys
import csv
import clr
clr.AddReference("System.IO")
from System.IO import FileNotFoundException
from .cpu import CPU
from rethebes.instrulib import Instrument

class Sensor(Instrument):
    def __init__(self, name, context, configuration):
        self.configuration = configuration
        super().__init__(name, context)

    def open(self):
        self.sampling_interval = self.configuration["sampling_interval"]
        self.should_write = self.configuration["write"]  

        if self.should_write:
            self.file = open(self.configuration["file_name"], "w", newline="")
            self.writer = csv.writer(self.file, delimiter=',')
            self.header_written = False  

        if "lhm_path" in self.configuration:
            sys.path.append(self.configuration["lhm_path"])
        try:
            clr.AddReference('LibreHardwareMonitorLib')
            from LibreHardwareMonitor import Hardware
        except (ImportError, FileNotFoundException):
            self.process_internal_error("""LibreHardwareMonitorLib could not be loaded.
                                           Check that it is installed and its directory is in the PYTHONPATH environment variable.
                                           Alternatively, add its path to the sensor.lhm_path variable in your rethebes config.""")
            return
        
        self.pc = Hardware.Computer()
        self.pc.IsCpuEnabled=True
        self.pc.Open()
        self.cpu = CPU(self.pc.Hardware[0])

        # Test reading
        test_read = self.cpu.read()
        if not bool(test_read):
            self.process_internal_error("Reading sensors failed. Check your LHM installation.")
        elif test_read["Temperature CPU Package"] is None:
            msg = "Could not read temperature. This is most likely due to rethebes not running with elevated privileges. Please re-execute in an elevated terminal."
            if "accept_incomplete_data" in self.configuration and self.configuration["accept_incomplete_data"]:
                logging.warning(msg)
            else:
                self.process_internal_error(msg)

    def close(self):
        if self.should_write:
            self.file.close()

    def run(self):
        stop_period = time.time() + self.sampling_interval
        self.act()
        time.sleep(max(0, stop_period-time.time()))

    def act(self):
        values = {"Time": datetime.datetime.now().isoformat()}
        values.update(self.cpu.read())
        if self.should_write:
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
        for s in self.sockets.values():
            s.send_json(event)
