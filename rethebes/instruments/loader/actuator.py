"""
Part of the module that loads CPU cores, this class generates CPU load by tuning the sleep time.
Based on https://github.com/GaetanoCarlucci/CPULoadGenerator/.
Since the latter is MIT licensed, we include here the copyright notice, this subpackage is also MIT licensed.

Authors: Gaetano Carlucci, Giuseppe Cofano.
License: See package-level license file.
"""

import time

class Actuator:
    def __init__(self, controller, monitor, duration, target):
        self.controller = controller
        self.monitor = monitor
        self.duration = duration
        self.target = target
        self.controller.set_cpu(self.monitor.get_cpu_load())
        self.period = 0.05  # actuation period  in seconds
        self.start_time = time.time()

    def close(self):
        pass  # NOOP

    def generate_load(self, sleep_time):
        interval = time.time() + self.period - sleep_time
        # generates some getCpuLoad for interval seconds
        while time.time() < interval:
            pr = 213123  # generates some load
            _ = pr * pr
            pr = pr + 1

        time.sleep(sleep_time)

    def run(self):
        sleep_time = 0

        while self.duration < 0 \
                or (time.time() - self.start_time) <= self.duration:
            self.controller.set_cpu(self.monitor.get_cpu_load())
            sleep_time = self.controller.get_sleep_time()
            self.generate_load(sleep_time)
        return sleep_time

    def run_sequence(self, sequence):
        for cpuTarget in sequence:
            step_period = time.time() + 4
            self.controller.set_cpu_target(cpuTarget)
            self.monitor.set_cpu_target(cpuTarget)
            while time.time() < step_period:
                self.controller.set_cpu(self.monitor.get_cpu_load())
                sleep_time = self.controller.get_sleep_time()
                self.generate_load(sleep_time)
                self.monitor.set_sleep_time(sleep_time)

