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
from matplotlib import colormaps

from .util import (
    analyze_temp_vs_load,
    analyze_temp_vs_power,
    check_if_data_complete,
    hex_string_from_rgba,
    read_data_from_file,
)


def format_base_axis(axis):
    axis.grid()
    axis.legend()
    axis.autoscale(tight=True)


def plot_temp_vs_load(data, axis, name=None, color=None, alpha=None):
    delta_t = data["Time"].diff().mean() / np.timedelta64(1, "s")
    window = int(10 / delta_t)
    axis.plot(
        data["Load CPU Total"].rolling(window).mean(),
        data["Temperature Core Average"].rolling(window).mean(),
        marker=".",
        color=color,
        alpha=alpha,
        linestyle="none",
        label=name,
    )
    axis.set_xlabel("Load CPU Total [%]")
    axis.set_ylabel("Temperature [°C]")


def plot_temp_vs_power(data, axis, name=None, color=None, alpha=None):
    delta_t = data["Time"].diff().mean() / np.timedelta64(1, "s")
    window = int(10 / delta_t)
    axis.plot(
        data["Power CPU Cores"].rolling(window).mean(),
        data["Temperature Core Average"].rolling(window).mean(),
        marker=".",
        color=color,
        alpha=alpha,
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


def series_plots(file_names, data_list):
    fig = plt.figure()
    ax_temp_vs_load = fig.add_subplot(121)
    ax_temp_vs_power = fig.add_subplot(122)
    threshold = 4
    num = len(file_names)
    if num <= threshold:
        for name, data in zip(file_names, data_list):
            plot_temp_vs_load(data, ax_temp_vs_load, Path(name).stem)
            plot_temp_vs_power(data, ax_temp_vs_power, Path(name).stem)
    else:
        # Use a colormap to distinguish the different series
        cmap = colormaps["winter"]
        for i, (name, data) in enumerate(zip(file_names, data_list)):
            color_string = hex_string_from_rgba(*cmap(i / (num - 1)))
            if i == 0 or i == num - 1:
                plot_temp_vs_load(
                    data,
                    ax_temp_vs_load,
                    name=Path(name).stem,
                    color=color_string,
                    alpha=0.5,
                )
                plot_temp_vs_power(
                    data,
                    ax_temp_vs_power,
                    name=Path(name).stem,
                    color=color_string,
                    alpha=0.5,
                )
            else:
                plot_temp_vs_load(data, ax_temp_vs_load, color=color_string, alpha=0.5)
                plot_temp_vs_power(
                    data, ax_temp_vs_power, color=color_string, alpha=0.5
                )
    format_base_axis(ax_temp_vs_load)
    format_base_axis(ax_temp_vs_power)
    fig.tight_layout()


def history_plots(file_names, data_list):
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
    # Plot line and marker separately to have different alpha
    ax_t.plot(xrange, df["t_for_l95"], marker=".", linestyle="none", color="blue")
    ax_t.plot(xrange, df["t_for_l95"], marker="none", alpha=0.5, color="blue")
    ax_c.plot(xrange, df["c"], marker=".", linestyle="none", color="blue")
    ax_c.plot(xrange, df["c"], marker="none", alpha=0.5, color="blue")
    ax_t.set_ylabel("T for L95 [°C]")
    ax_c.set_ylabel("C [W/K]")
    ax_t.grid()
    ax_c.grid()
    if len(xrange_as_dates) == len(xrange_as_names):
        ax_t.set_xlabel("File time")
        ax_c.set_xlabel("File time")
        locator = mdates.AutoDateLocator()
        formatter = mdates.AutoDateFormatter(locator)
        ax_t.xaxis.set_major_locator(locator)
        ax_t.xaxis.set_major_formatter(formatter)
        ax_c.xaxis.set_major_locator(locator)
        ax_c.xaxis.set_major_formatter(formatter)
        for label in ax_t.get_xticklabels(which="major") + ax_c.get_xticklabels(
            which="major"
        ):
            label.set(rotation=30, horizontalalignment="right")
    else:
        ax_t.set_xlabel("File name")
        ax_c.set_xlabel("File name")
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
    series_plots(file_names, data_list)
    history_plots(file_names, data_list)
    plt.show()
