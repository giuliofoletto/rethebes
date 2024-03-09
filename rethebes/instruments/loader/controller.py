"""
Part of the module that loads CPU cores, this class controls the CPU status.
Based on https://github.com/GaetanoCarlucci/CPULoadGenerator/.
Since the latter is MIT licensed, we include here the copyright notice, this subpackage is also MIT licensed.

Authors: Gaetano Carlucci, Giuseppe Cofano.
License: See package-level license file.
"""

import time
from threading import Event, RLock, Thread


class ControllerThread(Thread):
    def __init__(self, sampling_interval=0.1, reference_period=0.1, ki=None, kp=None):
        # Synchronization variables
        self.shutdown_flag = Event()
        self.sleep_lock = RLock()
        self.cpu_lock = RLock()
        self.target_lock = RLock()

        self.sampling_interval = sampling_interval
        self.reference_period = (
            reference_period  # actuation period and reference for the sleep time
        )
        self.sleep_time = 0.02  # this is controller output and represents the sleep time to achieve the requested CPU load
        self.cpu_period = 0.03  # time of not sleep (cpu period + sleep time = period)
        self.alpha = 0.2  # filter coefficient
        self.cpu_target = 0.20  # target CPU load should be provided as input (modified by parent object)
        self.cpu_load = 0  # current CPU load returned from the Monitor thread
        if ki is None:
            self.ki = 0.2  # integral constant of th PI regulator
        if kp is None:
            self.kp = 0.02  # proportional constant of th PI regulator
        self.int_err = 0  # integral error (initialized to 0)
        self.last_ts = time.time()  # last sampled time
        self.err = 0  # current error
        super(ControllerThread, self).__init__()

    def stop(self):
        self.shutdown_flag.set()

    def get_sleep_time(self):
        with self.sleep_lock:
            return self.sleep_time

    def set_sleep_time(self, sleep_time):
        with self.sleep_lock:
            self.sleep_time = sleep_time

    def get_cpu_target(self):
        with self.target_lock:
            return self.cpu_target

    def set_cpu_target(self, cpu_target):
        with self.target_lock:
            self.cpu_target = cpu_target

    def set_cpu_load(self, cpu_load):
        with self.cpu_lock:
            # Apply first order filter to the measurement samples
            self.cpu_load = self.alpha * cpu_load + (1 - self.alpha) * self.cpu_load

    def get_cpu_load(self):
        with self.cpu_lock:
            return self.cpu_load

    def run(self):
        def calculate_output_sleep_time(cpu_period):
            sleep_time = self.reference_period - cpu_period
            return sleep_time

        self.shutdown_flag.clear()
        while not self.shutdown_flag.is_set():
            # Must be the same sampling interval of monitor
            time.sleep(self.sampling_interval)

            # get all variables
            with self.target_lock, self.cpu_lock:
                cpu_target = self.cpu_target
                cpu_load = self.cpu_load

            # Note that if the cpu_load is too high, the error is negative
            # This leads to a decrease of cpu_period and in turn to an increase of sleep_time
            self.err = cpu_target - cpu_load  # current error
            ts = time.time()

            samp_int = ts - self.last_ts  # sample interval
            self.int_err = self.int_err + self.err * samp_int  # integral error
            self.last_ts = ts
            self.cpu_period = self.kp * self.err + self.ki * self.int_err

            # anti wind up control
            if self.cpu_period < 0:
                self.cpu_period = 0
                self.int_err = self.int_err - self.err * samp_int
            if self.cpu_period > self.reference_period:
                self.cpu_period = self.reference_period
                self.int_err = self.int_err - self.err * samp_int

            self.set_sleep_time(calculate_output_sleep_time(self.cpu_period))
