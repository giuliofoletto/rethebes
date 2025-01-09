"""
Function to compare the results of multiple measurements.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import datetime
import logging
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .util import (
    analyze_temp_vs_load,
    analyze_temp_vs_power,
    check_if_data_complete,
    read_data_from_file,
)


def format_base_axis(axis):
    axis.grid()
    axis.legend()
    axis.autoscale(tight=True)


def plot_temp_vs_load(data, axis, name=""):
    delta_t = data["Time"].diff().mean() / np.timedelta64(1, "s")
    window = int(10 / delta_t)
    axis.plot(
        data["Load CPU Total"].rolling(window).mean(),
        data["Temperature Core Average"].rolling(window).mean(),
        marker=".",
        linestyle="none",
        label=name,
    )
    axis.set_xlabel("Load CPU Total [%]")
    axis.set_ylabel("Temperature [°C]")


def plot_temp_vs_power(data, axis, name=""):
    delta_t = data["Time"].diff().mean() / np.timedelta64(1, "s")
    window = int(10 / delta_t)
    axis.plot(
        data["Power CPU Cores"].rolling(window).mean(),
        data["Temperature Core Average"].rolling(window).mean(),
        marker=".",
        linestyle="none",
        label=name,
    )
    axis.set_xlabel("Power CPU Cores [W]")
    axis.set_ylabel("Temperature [°C]")


def analyze_historical_data(file_names, data_list):
    t_for_l95_list = []
    c_list = []
    for data in data_list:
        t_for_l95 = analyze_temp_vs_load(data)["t_for_l95"]
        c = analyze_temp_vs_power(data)["c"]
        t_for_l95_list.append(t_for_l95)
        c_list.append(c)
    df = pd.DataFrame({"t_for_l95": t_for_l95_list, "c": c_list}, index=file_names)
    return df


def all_plots(file_names, data_list):
    fig = plt.figure()
    ax_temp_vs_load = fig.add_subplot(121)
    ax_temp_vs_power = fig.add_subplot(122)
    for name, data in zip(file_names, data_list):
        plot_temp_vs_load(data, ax_temp_vs_load, Path(name).stem)
        plot_temp_vs_power(data, ax_temp_vs_power, Path(name).stem)
    format_base_axis(ax_temp_vs_load)
    format_base_axis(ax_temp_vs_power)
    fig.tight_layout()

    figh = plt.figure()
    ax_t = figh.add_subplot(121)
    ax_c = figh.add_subplot(122)
    df = analyze_historical_data(file_names, data_list)
    xrange_as_names = []
    xrange_as_dates = []
    for file_name in file_names:
        xrange_as_names.append(Path(file_name).stem)
        try:
            xrange_as_dates.append(
                datetime.datetime.strptime(Path(file_name).stem, "%Y-%m-%d-%H-%M-%S")
            )
        except ValueError:
            pass
    if len(xrange_as_dates) == len(xrange_as_names):
        xrange = xrange_as_dates
    else:
        xrange = xrange_as_names
    ax_t.plot(xrange, df["t_for_l95"], marker=".")
    ax_c.plot(xrange, df["c"], marker=".")
    ax_t.set_xlabel("File name")
    ax_t.set_ylabel("T for L95 [°C]")
    ax_c.set_xlabel("File name")
    ax_c.set_ylabel("C [W/K]")
    ax_t.grid()
    ax_c.grid()
    ax_t.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d-%H-%M-%S"))
    ax_c.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d-%H-%M-%S"))
    figh.tight_layout()


def compare(file_names):
    # Check if all files are complete
    data_list = []
    for file_name in file_names:
        data_list.append(read_data_from_file(file_name))
    complete = [check_if_data_complete(d) for d in data_list]
    if not all(complete):
        logging.critical("Can only run the comparison on complete data")
        return
    all_plots(file_names, data_list)
    plt.show()
