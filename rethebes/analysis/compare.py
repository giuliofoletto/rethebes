"""
Function to compare the results of multiple measurements.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import logging
import os

from .util import *


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


def all_plots(file_names, data_list):
    fig = plt.figure()
    ax_temp_vs_load = fig.add_subplot(121)
    ax_temp_vs_power = fig.add_subplot(122)
    for name, data in zip(file_names, data_list):
        plot_temp_vs_load(
            data, ax_temp_vs_load, os.path.splitext(os.path.basename(name))[0]
        )
        plot_temp_vs_power(
            data, ax_temp_vs_power, os.path.splitext(os.path.basename(name))[0]
        )
    format_base_axis(ax_temp_vs_load)
    format_base_axis(ax_temp_vs_power)
    fig.tight_layout()


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
