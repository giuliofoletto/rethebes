"""
Holder for CPU sensors.
Note: to find out the correct indexes of the sensor use
for i in range(50): # arbitrary big number
    print(i, self.hw.Sensors[i].Name, self.hw.Sensors[i].SensorType)

Authors: Giulio Foletto.
License: See project-level license file.
"""


class CPU:
    def __init__(self, hw):
        self.hw = hw
        self.latest_values = {}
        self.discover_sensors()

    def read(self):
        self.hw.Update()
        for key, index in self.sensors.items():
            self.latest_values[key] = self.hw.Sensors[index].Value
        return self.latest_values

    def discover_sensors(self):
        self.hw.Update()
        index = 0
        self.sensors = dict()
        while True:
            try:
                name = str(self.hw.Sensors[index].Name)
                stype = str(self.hw.Sensors[index].SensorType)
            except IndexError:
                break
            # Accept all sensors
            # But here is where we could put some rules to discard some
            self.sensors[stype + " " + name] = index
            index += 1
