from manager import Manager
from loader import Loader
from sensor import Sensor
import zmq
import datetime

OUTPUT_DIR = "./output/"

def process_configuration(configuration):
    # Allow automatic list of instruments
    if "instruments" not in configuration["manager"] or configuration["manager"]["instruments"] == "auto":
        configuration["manager"]["instruments"] = []
        for k in configuration:
            if k != "manager":
                configuration["manager"]["instruments"].append(k)
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

    manager.main()
    
    context.term()
