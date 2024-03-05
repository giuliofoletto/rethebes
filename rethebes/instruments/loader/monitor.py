"""
Part of the module that loads CPU cores, this class monitors the CPU status.
Based on https://github.com/GaetanoCarlucci/CPULoadGenerator/.
Since the latter is MIT licensed, we include here the copyright notice, this subpackage is also MIT licensed.

Authors: Gaetano Carlucci, Giuseppe Cofano.
License: See package-level license file.
"""

import os
import time
from threading import Event, RLock, Thread

import psutil


class MonitorThread(Thread):
    def __init__(self, cpu_core, interval):
        # Synchronization variables
        self.shutdown_flag = Event()
        self.sleep_lock = RLock()
        self.cpu_lock = RLock()

        self.cpu_core = cpu_core  # unused currently
        self.sampling_interval = interval  # sample time interval
        self.sample = 0.5  # cpu load measurement sample (with useless initial value)
        self.cpu_load = 0.5  # cpu load filtered (with useless initial value)
        self.alpha = 1  # filter coefficient
        self.sleep_time = 0.03  # useful only for Actuator.run_sequence, which is unused
        self.sleep_time_target = 0.03  # useful only for Actuator.run_sequence, which is unused
        self.cpu_target = 0.5  # useful only for Actuator.run_sequence, which is unused

        super(MonitorThread, self).__init__()

    def stop(self):
        self.shutdown_flag.set()

    def get_cpu_load(self):
        with self.cpu_lock:
            return self.cpu_load

    def set_cpu_load(self, cpu_load):
        with self.cpu_lock:
            # Apply first order filter to the measurement samples
            self.cpu_load = self.alpha * cpu_load + (1 - self.alpha) * self.cpu_load

    def set_sleep_time_target(self, sleep_time_target):
        self.sleep_time_target = sleep_time_target

    def set_sleep_time(self, sleep_time):
        with self.sleep_lock:
            self.sleep_time = sleep_time

    def set_cpu_target(self, cpu_target):
        self.cpu_target = cpu_target

    def run(self):
        p = psutil.Process(os.getpid())
        self.shutdown_flag.clear()
        while not self.shutdown_flag.is_set():
            # Get the cpu utilization percentage, by the current process
            # in the interval of length self.sampling_interval (blocking)
            self.sample = p.cpu_percent(self.sampling_interval)
            self.set_cpu_load(self.sample)
