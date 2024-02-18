"""
Note: to find out the correct indexes of the sensor use
for i in range(50): # arbitrary big number
    print(i, self.hw.Sensors[i].Name, self.hw.Sensors[i].SensorType)
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
            if stype == "Load" and ("CPU Core #" in name or "CPU Total" in name):
                self.sensors[stype + " " + name] = index
            elif stype == "Temperature" and "Distance" not in name and "Max" not in name and "Average" not in name:
                self.sensors[stype + " " + name] = index
            elif stype == "Clock" and "CPU Core" in name:
                self.sensors[stype + " " + name] = index
            elif stype == "Power" and ("Cores" in name or "Package" in name):
                self.sensors[stype + " " + name] = index
            index += 1
