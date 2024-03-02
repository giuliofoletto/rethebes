"""
App logic.

Authors: Giulio Foletto.
"""

import datetime
import zmq
from manager import Manager
from loader import Loader
from sensor import Sensor
from .default_configuration import default_configuration

OUTPUT_DIR = "./output/"

def process_configuration(configuration):
    # Allow automatic list of instruments
    if "instruments" not in configuration or configuration["instruments"] == "auto":
        configuration["instruments"] = []
        known_instruments = ["sensor", "loader"]
        for k in known_instruments:
            if k in configuration:
                configuration["instruments"].append(k)
    # Allow loading of settings from default
    for k in configuration["instruments"]:
        if k not in configuration:
            configuration[k] = default_configuration[k]
    # Allow auto setting of file name
    if "sensor" in configuration and ("file_name" not in configuration["sensor"] or configuration["sensor"]["file_name"] == "auto"):
        configuration["sensor"]["file_name"] = OUTPUT_DIR + datetime.datetime.now().isoformat(sep = "-", timespec="seconds").replace(":", "-") + ".csv"
    return configuration

def main(configuration):
    configuration = process_configuration(configuration)
    context = zmq.Context(0)
    sensor = Sensor("sensor", context, configuration["sensor"])
    loader = Loader("loader", context, configuration["loader"])
    manager = Manager("director", context, [sensor, loader])
    # This executes everything
    manager.main()    
    context.term()
