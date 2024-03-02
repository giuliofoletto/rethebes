"""
Module that loads CPU cores.
Based on https://github.com/GaetanoCarlucci/CPULoadGenerator/ 

Authors: Gaetano Carlucci, Giuseppe Cofano, Giulio Foletto.
"""

import os
import json
import multiprocessing
import itertools
import logging
import psutil
from .actuator import Actuator
from .controller import ControllerThread
from .monitor import MonitorThread
from rethebes.util import Instrument, configure_logging

class Loader(Instrument):
    def __init__(self, name, context, configuration):
        self.configuration = configuration
        super().__init__(name, context)

    def open(self):
        self.physical_cores = psutil.cpu_count(logical=False)
        self.logical_cores = psutil.cpu_count(logical=True)
        self.hyperthreading = self.logical_cores // self.physical_cores

    def run(self):
        for load in self.configuration:
            # This is a long running operation, so we need to check state often
            self.listen(0)
            if self.get_state() != "running":
                break
            # Preprocess load at interface level
            # Allow loading all cores with "all"
            if load["target_cores"] == "all":
                load["target_cores"] = []
                for i in range(self.physical_cores):
                    load["target_cores"].append(i+1)
            # Allow setting one load for the selected cores
            if not isinstance(load["target_loads"], list):
                value = load["target_loads"]
                load["target_loads"] = []
                for i in range(len(load["target_cores"])):
                    load["target_loads"].append(value)
            logging.info("Starting load: " + json.dumps(load))
            self.send_event(command = "start", **load)

            # Preprocess load at working level
            target_cores = []
            target_loads = []
            duration = load["duration"]
            sampling_interval = load["sampling_interval"]
            
            # Internally, cores are grouped as two due to hyperthreading
            # At interface level, we want 1-6
            # We load a process for each of the two logical threads of each core
            for i in range(len(load["target_cores"])):
                for j in range(self.hyperthreading):
                    target_cores.append(2*(load["target_cores"][i]-1) + j)

            for i in range(len(load["target_loads"])):
                # We attribute the requested load to each of the two logical threads
                # Recent LHM reports load per thread, so this is consistent
                for j in range(self.hyperthreading):
                    target_loads.append(load["target_loads"][i]*1/100)

            with multiprocessing.Pool(len(target_cores)) as pool:
                pool.starmap(load_core, zip(
                    target_cores,
                    target_loads,
                    itertools.repeat(duration),
                    itertools.repeat(sampling_interval)
                ))
            self.send_event(command = "stop", **load)
        self.send_event(command = "finish")


def load_core(target_core, target_load, duration=-1, sampling_interval=0.1):
    # Reconfigure this as logging lives per process
    configure_logging()

    # lock this process to the target core
    process = psutil.Process(os.getpid())
    process.cpu_affinity([target_core])

    monitor = MonitorThread(target_core, sampling_interval)
    control = ControllerThread(sampling_interval)
    control.set_cpu_target(target_load)

    actuator = Actuator(control, monitor, duration, target_core)

    try:
        monitor.start()
        control.start()
        actuator.run()
    except KeyboardInterrupt:
        logging.warning("Subprocess terminated due to CTRL+C event")
    except:
        logging.warning("Subprocess terminated due to exception")
    finally:
        actuator.close()
        monitor.stop()
        control.stop()
        monitor.join()
        control.join()