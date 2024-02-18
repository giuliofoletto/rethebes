class CPU:
    def __init__(self, hw):
        self.hw = hw
        self.latest_values = {}        

        self.sensors = {
            "Load 1": 0,
            "Load 2": 1,
            "Load 3": 2,
            "Load 4": 3,
            "Load 5": 4,
            "Load 6": 5,
            "Load Total": 6,
            "Temp 1": 7,
            "Temp 2": 8,
            "Temp 3": 9,
            "Temp 4": 10,
            "Temp 5": 11,
            "Temp 6": 12,
            "Temp Package": 13,
            "Frequency 1": 22,
            "Frequency 2": 23,
            "Frequency 3": 24,
            "Frequency 4": 25,
            "Frequency 5": 26,
            "Frequency 6": 27,
            "Power Package": 28,
            "Power Cores": 29
        }

    def read(self):
        self.hw.Update()
        for key, index in self.sensors.items():
            self.latest_values[key] = self.hw.Sensors[index].Value
            if "Load" in key:
                self.latest_values[key] *= 2 # Because of HTT
        return self.latest_values
