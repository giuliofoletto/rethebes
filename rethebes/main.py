"""
Functions that define the app logic.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import datetime
import os

import zmq

from rethebes.analysis import analysis
from rethebes.instruments import Loader, Manager, Sensor, Timer

known_instruments = {"loader": Loader, "sensor": Sensor, "timer": Timer}

default_configuration = {
    "instruments": ["loader", "sensor"],
    "analyze": False,
    "loader": [
        {
            "target_cores": "all",
            "target_loads": 0,
            "duration": 5,
            "sampling_interval": 0.1,
        }
    ],
    "sensor": {
        "sampling_interval": 0.1,
        "accept_incomplete_data": False,
        "write": True,
        "file_name": "auto",
    },
    "timer": {"duration": 5},
}


def process_configuration(configuration):
    # Allow automatic list of instruments
    if "instruments" not in configuration or configuration["instruments"] == "auto":
        configuration["instruments"] = default_configuration["instruments"]
    # Allow not including timer
    if (
        "loader" not in configuration["instruments"]
        and "timer" not in configuration["instruments"]
    ):
        configuration["instruments"].append("timer")
    # Allow automatic setting of master
    if "master" not in configuration:
        if "loader" in configuration["instruments"]:
            configuration["master"] = "loader"
        else:
            configuration["master"] = "timer"
    # Allow not setting analyze after run
    if "analyze" not in configuration:
        configuration["analyze"] = default_configuration["analyze"]
    # Allow loading of settings from default
    for instrument in configuration["instruments"]:
        if instrument not in configuration:
            configuration[instrument] = default_configuration[instrument]
        else:
            # Allow partial definition of settings
            if instrument != "loader":
                for k in default_configuration[instrument]:
                    if k not in configuration[instrument]:
                        configuration[instrument][k] = default_configuration[
                            instrument
                        ][k]
            else:
                default_load = default_configuration["loader"][0]
                for i, load in enumerate(configuration["loader"]):
                    for k in default_load:
                        if k not in load:
                            configuration["loader"][i][k] = default_load[k]
    # Allow auto setting of file name
    if "sensor" in configuration and (
        "file_name" not in configuration["sensor"]
        or configuration["sensor"]["file_name"] == "auto"
    ):
        file_name = (
            datetime.datetime.now()
            .isoformat(sep="-", timespec="seconds")
            .replace(":", "-")
            + ".csv"
        )
        configuration["sensor"]["file_name"] = os.path.join(
            get_default_output_directory(), file_name
        )
    return configuration


def get_default_global_directory(create=False):
    user_dir = os.path.expanduser("~")
    rethebes_dir = os.path.join(user_dir, ".rethebes")
    if create and not os.path.exists(rethebes_dir):
        os.makedirs(rethebes_dir)
    return rethebes_dir


def get_default_output_directory(create=False):
    rethebes_dir = get_default_global_directory()
    output_dir = os.path.join(rethebes_dir, "output")
    if create and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def get_default_config_directory(create=False):
    rethebes_dir = get_default_global_directory()
    config_dir = os.path.join(rethebes_dir, "config")
    if create and not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return config_dir


def main(configuration):
    configuration = process_configuration(configuration)
    context = zmq.Context(0)
    instruments = [
        known_instruments[i](i, context, configuration[i])
        for i in configuration["instruments"]
    ]
    manager = Manager("manager", context, instruments, configuration["master"])
    # This executes everything
    manager.main()
    context.term()
    if configuration["analyze"] and configuration["sensor"]["write"]:
        analysis(configuration["sensor"]["file_name"])
