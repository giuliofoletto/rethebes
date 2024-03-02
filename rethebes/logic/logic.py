"""
App logic.

Authors: Giulio Foletto.
"""

import datetime
import os
import zmq
from rethebes.manager import Manager
from rethebes.loader import Loader
from rethebes.sensor import Sensor
from .default_configuration import default_configuration

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
        configuration["sensor"]["file_name"] = str(get_default_output_directory()) + "/" + datetime.datetime.now().isoformat(sep = "-", timespec="seconds").replace(":", "-") + ".csv"
    return configuration

def get_default_global_directory():
    user_dir = os.path.expanduser("~")
    rethebes_dir = os.path.join(user_dir, "rethebes")
    if not os.path.exists(rethebes_dir):
        os.makedirs(rethebes_dir)
    return rethebes_dir

def get_default_output_directory():
    rethebes_dir = get_default_global_directory()
    output_dir = os.path.join(rethebes_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def get_default_config_directory():
    rethebes_dir = get_default_global_directory()
    config_dir = os.path.join(rethebes_dir, "config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return config_dir

def main(configuration):
    configuration = process_configuration(configuration)
    context = zmq.Context(0)
    sensor = Sensor("sensor", context, configuration["sensor"])
    loader = Loader("loader", context, configuration["loader"])
    manager = Manager("director", context, [sensor, loader])
    # This executes everything
    manager.main()    
    context.term()
