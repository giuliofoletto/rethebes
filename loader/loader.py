"""
Part of ...

Authors: Gaetano Carlucci, Giuseppe Cofano, Giulio Foletto
"""

import os
import psutil
import itertools

from .actuator import Actuator
from .controller import ControllerThread
from .monitor import MonitorThread

import multiprocessing
import datetime

class Loader():
    def __init__(self, configuration, event_queue):
        self.configuration = configuration
        self.event_queue = event_queue


    def run(self):
        for load in self.configuration:
            self.send_event(type = "start", **load)

            # Preprocess load
            target_cores = load["target_cores"]
            target_loads = load["target_loads"]
            duration = load["duration"]
            sampling_interval = load["sampling_interval"]
            try:
                _ = iter(target_cores)
            except TypeError:
                target_cores = list(target_cores)
            try:
                _ = iter(target_loads)
            except TypeError:
                target_loads = list(target_loads)
            # Internally, cores are grouped as two
            # At interface level, we want 1-6
            for i in range(len(target_cores)):
                target_cores[i] = 2*(target_cores[i]-1)
            # Internally, we want numbers between 0-2
            # At interface level, we want %
            for i in range(len(target_loads)):
                # Single threaded performance
                # Does not coincide with LHM percentage which accounts for hyperthreading
                # That is, 50% LHM means full core utilization by a single thread
                # The same thing is called 100% here
                target_loads[i] = target_loads[i]*1/100

            with multiprocessing.Pool(len(target_cores)) as pool:
                pool.starmap(load_core, zip(
                    target_cores,
                    target_loads,
                    itertools.repeat(duration),
                    itertools.repeat(sampling_interval)
                ))
            self.send_event(type = "stop", **load)
    
    def send_event(self, **kwargs):
        event = dict()
        event["header"] = "loader-event"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = kwargs
        self.event_queue.put(event)
            

def load_core(target_core, target_load, duration=-1, sampling_interval=0.1):

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
    except:
        print("Exception in main loader")
    finally:
        actuator.close()
        monitor.stop()
        control.stop()
        monitor.join()
        control.join()