import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

date_format = mdates.DateFormatter('%H:%M:%S')

def get_number_of_cores(data):
    return (",").join(list(data.columns)).count("Temperature CPU Core") // 2 # //2 because of presence of distance to tjmax

def get_best_tick_interval(data):
    tot_time = (data["Time"].max() - data["Time"].min())/(np.timedelta64(1, "s"))
    if tot_time > 10:
        tick_interval = int(tot_time/10)
    else:
        tick_interval = 1
    return tick_interval

def get_columns_for_labels(num_labels):
    if num_labels <= 3:
        return num_labels
    if num_labels % 2 == 0:
        return num_labels // 2
    else:
        return (num_labels + 1) // 2

def format_standard_axis(data, axis):
    axis.autoscale(tight = True)
    axis.grid()
    _, labels = axis.get_legend_handles_labels()
    axis.legend(ncol=get_columns_for_labels(len(labels)), loc='center', bbox_to_anchor=(0.5, 1.06), fontsize = "x-small")
    axis.xaxis.set_major_formatter(date_format)
    axis.xaxis.set_major_locator(mdates.SecondLocator(interval=get_best_tick_interval(data)))
    axis.set_xlabel("Time")

def plot_frequency(data, axis):
    num_cores = get_number_of_cores(data)
    for i in range(num_cores):
        axis.plot(data["Time"], data["Clock CPU Core #" + str(i+1)], label = "C" + str(i+1))
    axis.set_ylabel("Frequency [MHz]")
    format_standard_axis(data, axis)

def plot_load(data, axis):
    num_cores = get_number_of_cores(data)
    for i in range(num_cores):
        axis.plot(data["Time"], 0.5*data["Load CPU Core #" + str(i+1) + " Thread #1"] + 0.5*data["Load CPU Core #" + str(i+1) + " Thread #2"], label = "C" + str(i+1))
    axis.plot(data["Time"], data["Load CPU Total"], label = "Total", color = "k", alpha = 0.5)
    axis.set_ylabel("Load [%]")
    format_standard_axis(data, axis)

def plot_temperature(data, axis):
    num_cores = get_number_of_cores(data)
    for i in range(num_cores):
        axis.plot(data["Time"], data["Temperature CPU Core #" + str(i+1)], label = "C" + str(i+1))
    axis.plot(data["Time"], data["Temperature CPU Package"], label = "Package", color = "k", alpha = 0.5)
    axis.set_ylabel("Temperature [°C]")
    format_standard_axis(data, axis)

def plot_temperature_distance_to_tjmax(data, axis):
    num_cores = get_number_of_cores(data)
    for i in range(num_cores):
        axis.plot(data["Time"], data["Temperature CPU Core #" + str(i+1) + " Distance to TjMax"], label = "C" + str(i+1))
    axis.set_ylabel("Temperature dist to TjMax [°C]")
    axis.set_ylabel("Temperature [°C]")
    format_standard_axis(data, axis)

def plot_power(data, axis):
    axis.plot(data["Time"], data["Power CPU Cores"], label = "Cores")
    axis.plot(data["Time"], data["Power CPU Memory"], label = "Memory")
    axis.plot(data["Time"], data["Power CPU Package"], label = "Package", color = "k", alpha = 0.5)
    axis.set_ylabel("Power [W]")
    format_standard_axis(data, axis)

def plot_voltage(data, axis):
    num_cores = get_number_of_cores(data)
    for i in range(num_cores):
        axis.plot(data["Time"], data["Voltage CPU Core #" + str(i+1)], label = "C" + str(i+1))
    axis.set_ylabel("Voltage [W]")
    format_standard_axis(data, axis)

def plot_temp_vs_load(data, axis):
    delta_t = data["Time"].diff().mean()/np.timedelta64(1, "s")
    window = int(10 / delta_t)
    axis.scatter(data["Load CPU Total"].rolling(window).mean(), data["Temperature Core Average"].rolling(window).mean(), label = "Avg")
    axis.scatter(data["Load CPU Total"].rolling(window).mean(), data["Temperature Core Max"].rolling(window).mean(), label = "Max")
    axis.set_xlabel("Load CPU Total [%]")
    axis.set_ylabel("Temperature [°C]")
    axis.grid()
    axis.legend()
    axis.autoscale(tight=True)

def read_data_from_file(file_name):
    return pd.read_csv(file_name, delimiter = ",", parse_dates=["Time"])

def check_if_data_complete(data):
    return not data["Temperature CPU Package"].isnull().values.any()

def all_plots(data):
    fig = plt.figure()
    ax_load = fig.add_subplot(231)
    plot_load(data, ax_load)

    ax_freq = fig.add_subplot(232)
    plot_frequency(data, ax_freq)

    ax_voltage = fig.add_subplot(233)
    plot_voltage(data, ax_voltage)

    ax_temp = fig.add_subplot(234)
    plot_temperature(data, ax_temp)

    ax_temp_tjmax = fig.add_subplot(235)
    plot_temperature_distance_to_tjmax(data, ax_temp_tjmax)

    ax_power = fig.add_subplot(236)
    plot_power(data, ax_power)

    fig.autofmt_xdate()
    fig.tight_layout()
    
    fig2, ax_temp_vs_load = plt.subplots()
    plot_temp_vs_load(data, ax_temp_vs_load)
    fig2.tight_layout()

def plot_incomplete_data(data):
    fig = plt.figure()
    ax_load = fig.add_subplot(111)
    plot_load(data, ax_load)

    fig.autofmt_xdate()
    fig.tight_layout()

def analysis(file_name):
    data = read_data_from_file(file_name)

    if check_if_data_complete(data):
        all_plots(data)
    else:
        msg = """Temperature, frequencies, powers, and voltages are not present in data. 
                 This is most likely due to rethebes not running with elevated privileges.
                 Please measure (rethebes run) in an elevated terminal."""
        logging.warning(msg)
        plot_incomplete_data(data)

    plt.show()