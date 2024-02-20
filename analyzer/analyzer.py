import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class Analyzer():
    def __init__(self, file_name):
        self.file_name = file_name
        self.analyze()
        self.show()

    def analyze(self):
        myFmt = mdates.DateFormatter('%H:%M:%S')

        data = pd.read_csv(self.file_name, delimiter = ",", parse_dates=["Time"])

        tot_time = (data["Time"].max() - data["Time"].min())/(np.timedelta64(1, "s"))
        tick_interval = int(tot_time/10)
        delta_t = data["Time"].diff().mean()/np.timedelta64(1, "s")

        num_cores = 6
        all_axes = []

        fig = plt.figure()
        ax_load = fig.add_subplot(231)
        for i in range(num_cores):
            ax_load.plot(data["Time"], 0.5*data["Load CPU Core #" + str(i+1) + " Thread #1"] + 0.5*data["Load CPU Core #" + str(i+1) + " Thread #2"], label = "C" + str(i+1))
        ax_load.plot(data["Time"], data["Load CPU Total"], label = "Total", color = "k", alpha = 0.5)
        ax_load.set_ylabel("Load [%]")
        all_axes.append(ax_load)

        ax_freq = fig.add_subplot(232)
        for i in range(num_cores):
            ax_freq.plot(data["Time"], data["Clock CPU Core #" + str(i+1)], label = "C" + str(i+1))
        ax_freq.set_ylabel("Frequency [MHz]")
        all_axes.append(ax_freq)

        ax_temp = fig.add_subplot(234)
        for i in range(num_cores):
            ax_temp.plot(data["Time"], data["Temperature CPU Core #" + str(i+1)], label = "C" + str(i+1))
        ax_temp.plot(data["Time"], data["Temperature CPU Package"], label = "Package", color = "k", alpha = 0.5)
        ax_temp.set_ylabel("Temperature [°C]")
        all_axes.append(ax_temp)

        ax_temp_tjmax = fig.add_subplot(235)
        for i in range(num_cores):
            ax_temp_tjmax.plot(data["Time"], data["Temperature CPU Core #" + str(i+1) + " Distance to TjMax"], label = "C" + str(i+1))
        ax_temp_tjmax.set_ylabel("Temperature dist to TjMax [°C]")
        all_axes.append(ax_temp_tjmax)

        ax_power = fig.add_subplot(236)
        ax_power.plot(data["Time"], data["Power CPU Cores"], label = "Cores")
        ax_power.plot(data["Time"], data["Power CPU Memory"], label = "Memory")
        ax_power.plot(data["Time"], data["Power CPU Package"], label = "Package", color = "k", alpha = 0.5)
        ax_power.set_ylabel("Power [W]")
        all_axes.append(ax_power)

        ax_voltage = fig.add_subplot(233)
        for i in range(num_cores):
            ax_voltage.plot(data["Time"], data["Voltage CPU Core #" + str(i+1)], label = "C" + str(i+1))
        ax_voltage.set_ylabel("Voltage [W]")
        all_axes.append(ax_voltage)

        for ax in all_axes:
            ax.autoscale(tight = True)
            ax.grid()
            ax.legend()
            ax.xaxis.set_major_formatter(myFmt)
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=tick_interval))
            ax.set_xlabel("Time")


        fig.autofmt_xdate()

        fig2, ax_temp_vs_load = plt.subplots()
        window = int(10 / delta_t)
        ax_temp_vs_load.scatter(data["Load CPU Total"].rolling(window).mean(), data["Temperature Core Average"].rolling(window).mean(), label = "Avg")
        ax_temp_vs_load.scatter(data["Load CPU Total"].rolling(window).mean(), data["Temperature Core Max"].rolling(window).mean(), label = "Max")
        ax_temp_vs_load.set_xlabel("Load CPU Total [%]")
        ax_temp_vs_load.set_ylabel("Temperature [°C]")
        ax_temp_vs_load.grid()
        ax_temp_vs_load.legend()
        ax_temp_vs_load.autoscale(tight=True)

    def show(self):
        plt.tight_layout()
        plt.show()