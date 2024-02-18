"""
Note: to find out the correct indexes of the sensor use
for i in range(50): # arbitrary big number
    print(i, self.hw.Sensors[i].Name, self.hw.Sensors[i].SensorType)
"""

class CPU:
    def __init__(self, hw):
        self.hw = hw
        self.latest_values = {}        

        self.sensors = {
            "Load 1A": 0,
            "Load 1B": 1,
            "Load 2A": 2,
            "Load 2B": 3,
            "Load 3A": 4,
            "Load 3B": 5,
            "Load 4A": 6,
            "Load 4B": 7,
            "Load 5A": 8,
            "Load 5B": 9,
            "Load 6A": 10,
            "Load 6B": 11,
            "Load Total": 12,
            "Temp 1": 14,
            "Temp 2": 15,
            "Temp 3": 16,
            "Temp 4": 17,
            "Temp 5": 18,
            "Temp 6": 19,
            "Temp Package": 20,
            "Frequency 1": 29,
            "Frequency 2": 30,
            "Frequency 3": 31,
            "Frequency 4": 32,
            "Frequency 5": 33,
            "Frequency 6": 34,
            "Power Package": 35,
            "Power Cores": 36
        }

    def read(self):
        self.hw.Update()
        for key, index in self.sensors.items():
            self.latest_values[key] = self.hw.Sensors[index].Value
        return self.latest_values
