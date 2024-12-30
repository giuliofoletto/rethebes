"""
Util functions to read and analyze data files.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def read_data_from_file(file_name):
    return pd.read_csv(file_name, delimiter=",", parse_dates=["Time"])


def check_if_data_complete(data):
    return not data["Temperature CPU Package"].isnull().values.any()


date_format = mdates.DateFormatter("%H:%M:%S")


def get_number_of_cores(data):
    return (",").join(list(data.columns)).count(
        "Temperature CPU Core"
    ) // 2  # //2 because of presence of distance to tjmax


def get_best_tick_interval(data):
    tot_time = (data["Time"].max() - data["Time"].min()) / (np.timedelta64(1, "s"))
    if tot_time > 10:
        tick_interval = int(tot_time / 10)
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
    axis.autoscale(tight=True)
    axis.grid()
    _, labels = axis.get_legend_handles_labels()
    axis.legend(
        ncol=get_columns_for_labels(len(labels)),
        loc="center",
        bbox_to_anchor=(0.5, 1.06),
        fontsize="x-small",
    )
    axis.xaxis.set_major_formatter(date_format)
    axis.xaxis.set_major_locator(
        mdates.SecondLocator(interval=get_best_tick_interval(data))
    )
    axis.set_xlabel("Time")


def get_average_load_core(data, core_index):
    valid_columns = []
    for column in data.columns:
        if ("Load CPU Core #" + str(core_index) + " Thread #") in column:
            valid_columns.append(column)
    return data[valid_columns].mean(axis=1)
